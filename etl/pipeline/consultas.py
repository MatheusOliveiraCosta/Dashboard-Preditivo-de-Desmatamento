"""Leituras do banco usadas pelas etapas de agregados, projeção e insights."""
from collections import defaultdict

FONTE_PREFERIDA = "PRODES"


def localidades(conn) -> dict:
    """id -> {nome, tipo}."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, nome, tipo FROM localidade")
        return {i: {"nome": n, "tipo": t} for i, n, t in cur.fetchall()}


def series_desmatamento(conn) -> dict:
    """localidade_id -> {fonte, anos, valores}. Usa o PRODES; se a localidade não tiver
    PRODES, usa o MapBiomas (nunca mistura as duas fontes na mesma série)."""
    por_loc = defaultdict(lambda: defaultdict(list))
    with conn.cursor() as cur:
        cur.execute("SELECT localidade_id, fonte, ano, area_km2 FROM desmatamento_anual "
                    "ORDER BY localidade_id, ano")
        for loc, fonte, ano, area in cur.fetchall():
            por_loc[loc][fonte].append((ano, area))
    saida = {}
    for loc, fontes in por_loc.items():
        fonte = FONTE_PREFERIDA if FONTE_PREFERIDA in fontes else sorted(fontes)[0]
        pares = fontes[fonte]
        saida[loc] = {"fonte": fonte, "anos": [a for a, _ in pares], "valores": [v for _, v in pares]}
    return saida


def series_clima(conn) -> dict:
    """localidade_id -> {ano: (temperatura, precipitação)}, só anos com os dois valores."""
    saida = defaultdict(dict)
    with conn.cursor() as cur:
        cur.execute("SELECT localidade_id, ano, temperatura_media_c, precipitacao_mm "
                    "FROM dado_climatico WHERE temperatura_media_c IS NOT NULL "
                    "AND precipitacao_mm IS NOT NULL")
        for loc, ano, temp, prec in cur.fetchall():
            saida[loc][ano] = (temp, prec)
    return saida


def projecao_vigente(conn, localidade_id):
    """Pontos da projeção mais recente: [(ano_projetado, valor, inferior, superior)]."""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT ano_projetado, valor_projetado_km2, intervalo_inferior, intervalo_superior
               FROM projecao WHERE localidade_id = %s
                 AND ano_base = (SELECT MAX(ano_base) FROM projecao WHERE localidade_id = %s)
               ORDER BY ano_projetado""",
            (localidade_id, localidade_id),
        )
        return cur.fetchall()
