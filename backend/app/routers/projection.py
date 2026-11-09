from fastapi import APIRouter, HTTPException, Query

from app.db import query
from app.routers import common
from app.schemas import ProjectionOut, ProjecaoPonto, SeriePonto, VisaoProjecao

router = APIRouter()

ANOS_DE_HISTORICO = 6  # anos observados que acompanham a projeção no gráfico


def _visao(loc: dict, horizonte: int | None) -> VisaoProjecao:
    _, serie = common.serie_desmatamento(loc["id"])
    linhas = query(
        """SELECT ano_projetado, valor_projetado_km2, intervalo_inferior, intervalo_superior
           FROM projecao WHERE localidade_id = %s
             AND ano_base = (SELECT MAX(ano_base) FROM projecao WHERE localidade_id = %s)
           ORDER BY ano_projetado""",
        (loc["id"], loc["id"]),
    )
    if not serie or not linhas:
        raise HTTPException(
            404, f"Não há projeção para {loc['nome']}. Rode a etapa 'projecao' do ETL."
        )
    if horizonte:
        linhas = linhas[:horizonte]

    pontos = [ProjecaoPonto(ano=l["ano_projetado"], valor_projetado_km2=float(l["valor_projetado_km2"]),
                            intervalo_inferior=float(l["intervalo_inferior"]),
                            intervalo_superior=float(l["intervalo_superior"])) for l in linhas]
    texto = common.insight(loc["id"], "PROJECAO_TENDENCIA")
    estabilizacao = (texto["metricas"].get("estabilizacao") if texto else None)
    if estabilizacao and estabilizacao > pontos[-1].ano:
        estabilizacao = None  # fora do horizonte pedido

    return VisaoProjecao(
        serie_historica=[SeriePonto(ano=a, area_km2=v) for a, v in serie[-ANOS_DE_HISTORICO:]],
        projecao=pontos,
        ponto_estabilizacao=estabilizacao,
        insight=texto["texto"] if texto else None,
    )


@router.get("/projection", response_model=ProjectionOut, tags=["projecao"])
def projection(
    localidade: int | None = Query(None, description="id da localidade; ausente = só a visão geral"),
    horizonte: int | None = Query(None, ge=1, le=30, description="anos à frente (padrão: todos os calculados)"),
):
    """`geral` é o Brasil; `regional` só vem quando há uma localidade escolhida."""
    brasil = common.resolver_localidade(None)
    geral = _visao(brasil, horizonte)
    regional = None
    if localidade is not None and localidade != brasil["id"]:
        regional = _visao(common.resolver_localidade(localidade), horizonte)
    return ProjectionOut(geral=geral, regional=regional, atualizado_em=common.atualizado_em())
