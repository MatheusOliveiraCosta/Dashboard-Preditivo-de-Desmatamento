"""DADOS MOCK (fictícios, determinísticos) para a fase de fundação técnica.

nada aqui vem de prodes/mapbiomas/inmet quando o ETL estiver pronto
cada função pública deste módulo deve ser substituída por uma consulta do postgre
mantendo as mesmas assinaturas
"""
import zlib
from datetime import datetime, timezone
from random import Random
from statistics import StatisticsError, correlation, linear_regression, pstdev

ANO_MIN, ANO_MAX = 2004, 2024
ATUALIZADO_EM = datetime(2026, 8, 15, tzinfo=timezone.utc)

# codigo, nome, tipo, sigla_uf, regiao, área mock em 2004 (km²)
_LOCALIDADES = [
    ("amazonia", "Amazônia", "bioma", None, None, 27772),
    ("cerrado", "Cerrado", "bioma", None, None, 15000),
    ("mata-atlantica", "Mata Atlântica", "bioma", None, None, 800),
    ("caatinga", "Caatinga", "bioma", None, None, 3000),
    ("pampa", "Pampa", "bioma", None, None, 400),
    ("pantanal", "Pantanal", "bioma", None, None, 700),
    ("PA", "Pará", "estado", "PA", "Norte", 8500),
    ("MT", "Mato Grosso", "estado", "MT", "Centro-Oeste", 11800),
    ("AM", "Amazonas", "estado", "AM", "Norte", 1200),
    ("RO", "Rondônia", "estado", "RO", "Norte", 3000),
    ("MA", "Maranhão", "estado", "MA", "Nordeste", 1800),
    ("TO", "Tocantins", "estado", "TO", "Norte", 1200),
    ("BA", "Bahia", "estado", "BA", "Nordeste", 2000),
    ("GO", "Goiás", "estado", "GO", "Centro-Oeste", 2500),
]
_POR_CODIGO = {
    c[0]: {"codigo": c[0], "nome": c[1], "tipo": c[2], "sigla_uf": c[3], "regiao": c[4]}
    for c in _LOCALIDADES
}
_BASE = {c[0]: c[5] for c in _LOCALIDADES}
_BIOMAS = [c[0] for c in _LOCALIDADES if c[2] == "bioma"]

# Forma geral da curva (relativa a 2004): queda até 2012, alta até 2021, queda depois.
_FORMA = [(2004, 1.0), (2012, 0.25), (2021, 0.60), (2024, 0.40)]


def _forma(ano: int) -> float:
    for (a0, v0), (a1, v1) in zip(_FORMA, _FORMA[1:]):
        if a0 <= ano <= a1:
            return v0 + (v1 - v0) * (ano - a0) / (a1 - a0)
    return _FORMA[-1][1]


def _rng(chave: str) -> Random:
    # crc32 (e não hash()) para o resultado ser igual a cada execução
    return Random(zlib.crc32(chave.encode()))


def _serie_propria(codigo: str) -> dict[int, float]:
    rng = _rng(codigo)
    return {
        ano: round(_BASE[codigo] * _forma(ano) * rng.uniform(0.94, 1.06), 1)
        for ano in range(ANO_MIN, ANO_MAX + 1)
    }


def _serie_completa(codigo: str | None) -> dict[int, float]:
    """codigo=None significa Brasil = soma dos biomas."""
    if codigo is not None:
        return _serie_propria(codigo)
    series = [_serie_propria(b) for b in _BIOMAS]
    return {ano: round(sum(s[ano] for s in series), 1) for ano in range(ANO_MIN, ANO_MAX + 1)}


# ---------------- API pública do módulo ----------------
def listar_localidades() -> list[dict]:
    return list(_POR_CODIGO.values())


def obter_localidade(codigo: str) -> dict | None:
    return _POR_CODIGO.get(codigo)


def nome_regiao(codigo: str | None) -> str:
    return "Brasil" if codigo is None else _POR_CODIGO[codigo]["nome"]


def serie_desmatamento(codigo: str | None, inicio: int, fim: int) -> list[dict]:
    s = _serie_completa(codigo)
    return [{"ano": a, "area_km2": s[a]} for a in range(inicio, fim + 1)]


def kpi(codigo: str | None) -> dict:
    s = _serie_completa(codigo)
    atual, anterior = s[ANO_MAX], s[ANO_MAX - 1]
    return {
        "region": codigo or "BR",
        "area_desmatada_km2": atual,
        "variacao_percentual": round((atual - anterior) / anterior * 100, 1),
        "ano_referencia": ANO_MAX,
    }


def kpis(codigo: str | None) -> list[dict]:
    if codigo is not None:
        return [kpi(codigo)]
    return [kpi(None)] + [kpi(b) for b in _BIOMAS]


def serie_clima(codigo: str | None, inicio: int, fim: int) -> list[dict]:
    rng = _rng("clima-" + (codigo or "BR"))
    temp0 = 24.0 + rng.uniform(-2, 3)
    prec0 = 1500 + rng.uniform(-400, 600)
    desm = _serie_completa(codigo)
    out = []
    for ano in range(ANO_MIN, ANO_MAX + 1):
        temp = round(temp0 + 0.04 * (ano - ANO_MIN) + rng.uniform(-0.3, 0.3), 2)
        prec = round(prec0 - 6 * (ano - ANO_MIN) + rng.uniform(-80, 80), 1)
        if inicio <= ano <= fim:
            out.append({"ano": ano, "area_km2": desm[ano],
                        "temperatura_media_c": temp, "precipitacao_mm": prec})
    return out


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3:
        return None
    try:
        return round(correlation(xs, ys), 2)
    except StatisticsError:
        return None


def projetar(codigo: str | None, horizonte: int) -> list[dict]:
    """Regressão linear nos últimos 10 anos + faixa de incerteza que cresce com o horizonte."""
    s = _serie_completa(codigo)
    anos = list(range(ANO_MAX - 9, ANO_MAX + 1))
    ys = [s[a] for a in anos]
    slope, intercept = linear_regression(anos, ys)
    sd = pstdev([y - (intercept + slope * a) for a, y in zip(anos, ys)])
    out = []
    for h in range(1, horizonte + 1):
        ano = ANO_MAX + h
        valor = max(0.0, intercept + slope * ano)
        margem = 1.96 * sd * (1 + 0.25 * h)
        out.append({
            "ano": ano,
            "valor_km2": round(valor, 1),
            "intervalo_inferior": round(max(0.0, valor - margem), 1),
            "intervalo_superior": round(valor + margem, 1),
        })
    return out


# ---------------- Insights (texto mock) ----------------
# Na versão final virá da tabela `insight` (gerados pelo Gemini no ETL).
def insight_overview(codigo: str | None, serie: list[dict]) -> str:
    regiao = nome_regiao(codigo)
    ultimo = serie[-1]
    if len(serie) < 2:
        return f"Em {ultimo['ano']}, a área desmatada em {regiao} foi de {ultimo['area_km2']:.0f} km²."
    anterior = serie[-2]["area_km2"]
    var = (ultimo["area_km2"] - anterior) / anterior * 100
    verbo = "caiu" if var < 0 else "subiu"
    return (f"A área desmatada em {regiao} em {ultimo['ano']} {verbo} {abs(var):.0f}% "
            f"em relação a {serie[-2]['ano']}.")


def _forca(r: float | None) -> str:
    if r is None:
        return "indefinida"
    a = abs(r)
    return "fraca" if a < 0.3 else "moderada" if a < 0.7 else "forte"


def insight_clima(codigo: str | None, inicio: int, fim: int, corr_temp: float | None) -> str:
    if corr_temp is None:
        return "Período curto demais para calcular a correlação."
    return (f"Em {nome_regiao(codigo)}, de {inicio} a {fim}, a correlação entre desmatamento e "
            f"temperatura é {_forca(corr_temp)} ({corr_temp:.2f}). Correlação não prova que "
            f"um fenômeno causa o outro.")


def insight_projecao(codigo: str | None, proj: list[dict]) -> str:
    ult = proj[-1]
    return (f"Se a tendência recente se mantiver, a área desmatada em {nome_regiao(codigo)} "
            f"deve ficar perto de {ult['valor_km2']:.0f} km² em {ult['ano']} "
            f"(faixa de {ult['intervalo_inferior']:.0f} a {ult['intervalo_superior']:.0f} km²). "
            f"É uma projeção estatística simples, não uma previsão exata.")
