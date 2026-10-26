import re
import unicodedata
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from . import config

# Nomes de colunas aceitos (já normalizados: minúsculas, sem acento).
# Se seu arquivo usar outro nome, acrescente aqui.
CAND_LOCAL = ["estado", "uf", "state", "state_name", "nome", "bioma", "biome",
              "localidade", "name", "regiao"]
CAND_ANO = ["ano", "year"]
CAND_VALOR = ["area km2", "area_km2", "area_km", "area", "areakm", "incremento", "valor",
              "value", "area_ha", "hectares", "ha"]


def conectar():
    return psycopg2.connect(config.DATABASE_URL)


def normalizar(txt):
    txt = unicodedata.normalize("NFKD", str(txt))
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", txt).strip().lower()


def resolver_arquivo(caminho: Path) -> Path:
    for ext in (caminho.suffix, ".csv", ".xlsx", ".xls"):
        candidato = caminho.with_suffix(ext)
        if candidato.exists():
            return candidato
    raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")


def ler_tabela(caminho: Path) -> pd.DataFrame:
    caminho = resolver_arquivo(caminho)
    if caminho.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(caminho)  # primeira aba
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(caminho, sep=None, engine="python", encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Não consegui decodificar {caminho}")


def para_numero(serie: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype(float)
    s = serie.astype(str).str.strip()
    tem_virgula = s.str.contains(",", regex=False)
    convertido = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(s.where(~tem_virgula, convertido), errors="coerce")


def achar_coluna(df, candidatos, rotulo):
    mapa = {normalizar(c): c for c in df.columns}
    for cand in candidatos:
        if cand in mapa:
            return mapa[cand]
    raise KeyError(
        f"Coluna de {rotulo} não encontrada. Colunas do arquivo: {list(df.columns)}. "
        f"Ajuste CAND_* em etl/common.py."
    )


def para_longo(df: pd.DataFrame) -> pd.DataFrame:
    """Aceita formato longo (local, ano, valor) ou largo (local + colunas 2004, 2005...)."""
    col_local = achar_coluna(df, CAND_LOCAL, "localidade")
    try:
        col_ano = achar_coluna(df, CAND_ANO, "ano")
    except KeyError:
        col_ano = None

    if col_ano:
        col_valor = achar_coluna(df, CAND_VALOR, "valor")
        out = df[[col_local, col_ano, col_valor]].copy()
    else:
        cols_ano = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c).strip())]
        if not cols_ano:
            raise KeyError(f"Sem coluna de ano nem colunas por ano. Colunas: {list(df.columns)}")
        out = df.melt(id_vars=[col_local], value_vars=cols_ano,
                      var_name="ano", value_name="valor")
    out.columns = ["local", "ano", "valor"]
    out["ano"] = pd.to_numeric(out["ano"].astype(str).str.strip(), errors="coerce")
    out["valor"] = para_numero(out["valor"])
    return out.dropna()


def lookup_localidades(conn, tipo):
    """Mapa nome/sigla normalizados -> localidade.id para ESTADO ou BIOMA."""
    mapa = {}
    with conn.cursor() as cur:
        cur.execute("SELECT id, nome, sigla_uf FROM localidade WHERE tipo = %s", (tipo,))
        for id_, nome, sigla in cur.fetchall():
            mapa[normalizar(nome)] = id_
            if sigla:
                mapa[normalizar(sigla)] = id_
    return mapa


def carregar_desmatamento(conn, caminho, tipo, fonte, fator=1.0):
    try:
        resolver_arquivo(caminho)
    except FileNotFoundError:
        print(f"  [{fonte}/{tipo}] arquivo não encontrado, pulando: {caminho.name}")
        return 0

    df = para_longo(ler_tabela(caminho))
    df["ano"] = df["ano"].astype(int)
    df = df[(df["ano"] >= config.ANO_MIN) & (df["ano"] <= config.ANO_MAX)]

    lookup = lookup_localidades(conn, tipo)
    df["localidade_id"] = df["local"].map(lambda x: lookup.get(normalizar(x)))
    ignorados = sorted(df.loc[df["localidade_id"].isna(), "local"].astype(str).unique())
    if ignorados:
        print(f"  [{fonte}/{tipo}] localidades sem correspondência (ignoradas): {ignorados}")
    df = df.dropna(subset=["localidade_id"])
    df["localidade_id"] = df["localidade_id"].astype(int)

    df = df.groupby(["localidade_id", "ano"], as_index=False)["valor"].sum()
    df["valor"] = df["valor"] * fator
    df = df[df["valor"] >= 0]
    if df.empty:
        raise ValueError(f"Nenhuma linha válida em {caminho} ({fonte}/{tipo})")

    linhas = [(int(r.localidade_id), int(r.ano), float(r.valor), fonte)
              for r in df.itertuples()]
    sql = """
        INSERT INTO desmatamento_anual (localidade_id, ano, area_km2, fonte)
        VALUES %s
        ON CONFLICT (localidade_id, ano, fonte)
        DO UPDATE SET area_km2 = EXCLUDED.area_km2
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, linhas)
    return len(linhas)