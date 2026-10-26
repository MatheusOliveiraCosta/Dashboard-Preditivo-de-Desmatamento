"""Diagnóstico do INMET: confere duplicidade de arquivos e chuva mensal por estado.

Uso: docker compose run --rm etl python diagnostico_inmet.py
"""
import io

import pandas as pd

from pipeline.common import normalizar
from pipeline.etl_inmet import _arquivos_csv

UFS = {"AP", "RJ", "RR"}
ufs_vistas = set()


def ler(nome, conteudo):
    linhas = conteudo.decode("latin-1").splitlines()
    meta = {}
    for linha in linhas[:8]:
        chave, _, valor = linha.partition(";")
        meta[normalizar(chave).rstrip(":")] = valor.strip()
    uf = meta.get("uf", "").upper()
    ufs_vistas.add(uf)
    if uf not in UFS:
        return None
    df = pd.read_csv(io.StringIO("\n".join(linhas[8:])), sep=";", decimal=",",
                     low_memory=False)
    cols = {normalizar(c): c for c in df.columns}
    col_data = next((c for k, c in cols.items() if k.startswith("data")), None)
    col_prec = next((c for k, c in cols.items() if "precipitacao total" in k), None)
    if not (col_data and col_prec):
        return None
    data = pd.to_datetime(df[col_data], format="%Y/%m/%d", errors="coerce")
    data = data.fillna(pd.to_datetime(df[col_data], format="%d/%m/%Y", errors="coerce"))
    prec = pd.to_numeric(df[col_prec], errors="coerce")
    prec = prec.where(prec > -9990)
    d = pd.DataFrame({"mes": data.dt.to_period("M").astype(str), "prec": prec})
    g = d.groupby("mes")["prec"].agg(mm="sum", horas="count").reset_index()
    g["arquivo"] = nome
    g["uf"] = uf
    g["codigo"] = meta.get("codigo (wmo)", "?")
    return g


partes = []
for nome, conteudo in _arquivos_csv():
    g = ler(nome, conteudo)
    if g is not None:
        partes.append(g)

print("UFs com estação nos arquivos:", sorted(u for u in ufs_vistas if u))
t = pd.concat(partes)

n = t.groupby(["codigo", "mes"])["arquivo"].nunique()
print(f"\n(estação, mês) em mais de um arquivo: {int((n > 1).sum())} de {len(n)}")
print(n[n > 1].reset_index().head(5).to_string(index=False))

s = t.groupby(["uf", "codigo", "mes"], as_index=False).agg(
    mm=("mm", "sum"), horas=("horas", "sum"))
tab = s.groupby(["mes", "uf"]).agg(
    mm=("mm", "mean"), horas=("horas", "mean"), est=("codigo", "nunique")).reset_index()
tab[["mm", "horas"]] = tab[["mm", "horas"]].round(0)
print("\nPor mês: chuva (mm) e horas com dado, médias por estação; nº de estações")
print(tab.pivot(index="mes", columns="uf", values=["mm", "horas", "est"]).to_string())
