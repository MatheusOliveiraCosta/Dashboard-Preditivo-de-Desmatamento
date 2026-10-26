import io
import zipfile

import pandas as pd
from psycopg2.extras import execute_values

from . import config
from .common import ler_tabela, lookup_localidades, normalizar

HORAS_ANO = 8760


def _arquivos_csv():
    for caminho in sorted(config.INMET_DIR.rglob("*")):
        sufixo = caminho.suffix.lower()
        if sufixo == ".zip":
            with zipfile.ZipFile(caminho) as z:
                for nome in z.namelist():
                    if nome.lower().endswith(".csv"):
                        yield nome, z.read(nome)
        elif sufixo == ".csv" and caminho.name != config.INMET_ESTACOES_BIOMA.name:
            yield caminho.name, caminho.read_bytes()


def _ler_estacao(conteudo: bytes):
    """CSV do BDMEP: 8 linhas de metadados, depois cabeçalho + dados horários."""
    linhas = conteudo.decode("latin-1").splitlines()
    meta = {}
    for linha in linhas[:8]:
        chave, _, valor = linha.partition(";")
        meta[normalizar(chave).rstrip(":")] = valor.strip()
    uf = meta.get("uf", "").upper()
    codigo = meta.get("codigo (wmo)", "")
    if not uf or not codigo:
        return None

    df = pd.read_csv(io.StringIO("\n".join(linhas[8:])), sep=";", decimal=",",
                     low_memory=False)
    cols = {normalizar(c): c for c in df.columns}
    col_data = next((c for k, c in cols.items() if k.startswith("data")), None)
    col_prec = next((c for k, c in cols.items() if "precipitacao total" in k), None)
    col_temp = next((c for k, c in cols.items()
                     if "temperatura do ar" in k and "bulbo seco" in k), None)
    if not (col_data and col_prec and col_temp):
        return None

    data = pd.to_datetime(df[col_data], format="%Y/%m/%d", errors="coerce")
    data = data.fillna(pd.to_datetime(df[col_data], format="%d/%m/%Y", errors="coerce"))
    data = data.fillna(pd.to_datetime(df[col_data], format="%Y-%m-%d", errors="coerce"))

    prec = pd.to_numeric(df[col_prec], errors="coerce")
    temp = pd.to_numeric(df[col_temp], errors="coerce")
    prec = prec.where(prec > -9990)  # -9999 = sem dado
    temp = temp.where(temp > -9990)

    d = pd.DataFrame({"ano_civil": data.dt.year, "mes": data.dt.month,
                      "prec": prec, "temp": temp}).dropna(subset=["ano_civil"])
    g = d.groupby(["ano_civil", "mes"]).agg(
        prec_soma=("prec", "sum"), prec_n=("prec", "count"),
        temp_soma=("temp", "sum"), temp_n=("temp", "count"),
    ).reset_index()
    g["ano_civil"] = g["ano_civil"].astype(int)
    g["mes"] = g["mes"].astype(int)
    g["uf"] = uf
    g["codigo"] = codigo
    return g


def _estacao_ano():
    partes = []
    for nome, conteudo in _arquivos_csv():
        try:
            g = _ler_estacao(conteudo)
        except Exception as e:  # um arquivo ruim não derruba o ETL
            print(f"  [INMET] ignorando {nome}: {e}")
            continue
        if g is not None:
            partes.append(g)
    if not partes:
        raise FileNotFoundError(f"Nenhum CSV do INMET válido em {config.INMET_DIR}")

    t = pd.concat(partes)

    # Zips podem trazer mais de um arquivo da mesma estação cobrindo o mesmo mês
    # (períodos sobrepostos). Somar contaria a chuva em dobro: fica o arquivo
    # mais completo de cada estação-mês.
    t["horas"] = t["prec_n"] + t["temp_n"]
    antes = len(t)
    t = (t.sort_values("horas", ascending=False)
         .drop_duplicates(["uf", "codigo", "ano_civil", "mes"]))
    if antes != len(t):
        print(f"  [INMET] {antes - len(t)} estação-mês repetidos em arquivos "
              f"sobrepostos (mantido o mais completo)")

    t["ano"] = t["ano_civil"]
    if config.CLIMA_ANO_PRODES:
        t["ano"] = t["ano_civil"] + (t["mes"] >= 8).astype(int)  # ago..jul -> ano seguinte

    t = (t.groupby(["uf", "codigo", "ano"], as_index=False)
         [["prec_soma", "prec_n", "temp_soma", "temp_n"]].sum())
    minimo = config.CLIMA_COBERTURA_MIN * HORAS_ANO
    t["precipitacao_mm"] = t["prec_soma"].where(t["prec_n"] >= minimo)
    t["temperatura_media_c"] = (t["temp_soma"] / t["temp_n"]).where(t["temp_n"] >= minimo)
    return t[t["ano"] >= config.ANO_MIN]


def _upsert(conn, df):
    df = df.dropna(subset=["precipitacao_mm", "temperatura_media_c"], how="all")
    linhas = []
    for r in df.itertuples():
        temp = None if pd.isna(r.temperatura_media_c) else round(float(r.temperatura_media_c), 2)
        prec = None if pd.isna(r.precipitacao_mm) else round(float(r.precipitacao_mm), 1)
        linhas.append((int(r.localidade_id), int(r.ano), temp, prec))
    if not linhas:
        return 0
    sql = """
        INSERT INTO dado_climatico
            (localidade_id, ano, temperatura_media_c, precipitacao_mm, fonte)
        VALUES %s
        ON CONFLICT (localidade_id, ano, fonte) DO UPDATE SET
            temperatura_media_c = EXCLUDED.temperatura_media_c,
            precipitacao_mm     = EXCLUDED.precipitacao_mm
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, linhas, template="(%s, %s, %s, %s, 'INMET')")
    return len(linhas)


def executar(conn):
    est = _estacao_ano()
    total = 0

    # Estados: média das estações da UF (precipitação = média dos totais anuais por estação)
    ufs = lookup_localidades(conn, "ESTADO")
    por_uf = (est.groupby(["uf", "ano"], as_index=False)
              [["precipitacao_mm", "temperatura_media_c"]].mean())
    por_uf["localidade_id"] = por_uf["uf"].map(lambda x: ufs.get(normalizar(x)))
    total += _upsert(conn, por_uf.dropna(subset=["localidade_id"]))

    # Biomas: precisa do lookup estação -> bioma (gerado uma vez, offline)
    if config.INMET_ESTACOES_BIOMA.exists():
        biomas = lookup_localidades(conn, "BIOMA")
        mapa = ler_tabela(config.INMET_ESTACOES_BIOMA)
        mapa.columns = [normalizar(c) for c in mapa.columns]
        mapa["codigo"] = mapa["codigo"].astype(str).str.strip()
        mapa["localidade_id"] = mapa["bioma"].map(lambda x: biomas.get(normalizar(x)))
        e = est.merge(mapa[["codigo", "localidade_id"]], on="codigo", how="inner")
        e = e.dropna(subset=["localidade_id"])
        por_bioma = (e.groupby(["localidade_id", "ano"], as_index=False)
                     [["precipitacao_mm", "temperatura_media_c"]].mean())
        total += _upsert(conn, por_bioma)
    else:
        print(f"  [INMET] {config.INMET_ESTACOES_BIOMA.name} não existe: biomas ignorados")

    return total