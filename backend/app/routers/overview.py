from fastapi import APIRouter, HTTPException, Query

from app.db import query
from app.routers import common
from app.schemas import Kpi, OverviewOut, SeriePonto
from app.services.indicadores import variacao_percentual

router = APIRouter()


def _bioma_critico(ano: int, fonte: str) -> str | None:
    """Bioma com a maior área desmatada no ano de referência."""
    linhas = query(
        """SELECT l.nome FROM desmatamento_anual d JOIN localidade l ON l.id = d.localidade_id
           WHERE l.tipo = 'BIOMA' AND d.ano = %s AND d.fonte = %s
           ORDER BY d.area_km2 DESC LIMIT 1""",
        (ano, fonte),
    )
    return linhas[0]["nome"] if linhas else None


@router.get("/overview", response_model=OverviewOut, tags=["overview"])
def overview(
    localidade: int | None = Query(None, description="id da localidade; ausente = Brasil"),
    ano_inicio: int | None = Query(None, ge=1900, le=2100),
    ano_fim: int | None = Query(None, ge=1900, le=2100),
):
    common.validar_periodo(ano_inicio, ano_fim)
    loc = common.resolver_localidade(localidade)
    fonte, serie = common.serie_desmatamento(loc["id"], ano_inicio, ano_fim)
    if not serie:
        raise HTTPException(404, f"Não há dados de desmatamento para {loc['nome']} no período pedido.")

    ano_ref, area_ref = serie[-1]
    anterior = next((area for ano, area in serie if ano == ano_ref - 1), None)
    regiao = {"PAIS": "BR", "ESTADO": loc["sigla_uf"], "BIOMA": loc["nome"]}[loc["tipo"]]
    texto = common.insight(loc["id"], "VISAO_GERAL")

    return OverviewOut(
        kpis=[Kpi(region=regiao or loc["nome"], area_desmatada_km2=area_ref,
                  variacao_percentual=variacao_percentual(area_ref, anterior), ano_referencia=ano_ref)],
        bioma_critico=_bioma_critico(ano_ref, fonte),
        serie_historica=[SeriePonto(ano=a, area_km2=v) for a, v in serie],
        insight=texto["texto"] if texto else None,
        atualizado_em=common.atualizado_em(),
    )
