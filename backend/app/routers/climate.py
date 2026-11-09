from fastapi import APIRouter, HTTPException, Query

from app.db import query
from app.routers import common
from app.schemas import ClimateCorrelationOut, ClimaPonto, IndicadoresClimaticos
from app.services.indicadores import correlacao, desvio_da_media, taxa_supressao_pct

router = APIRouter()


@router.get("/climate-correlation", response_model=ClimateCorrelationOut, tags=["clima"])
def climate_correlation(
    localidade: int | None = Query(None, description="id da localidade; ausente = Brasil"),
    ano_inicio: int | None = Query(None, ge=1900, le=2100),
    ano_fim: int | None = Query(None, ge=1900, le=2100),
):
    common.validar_periodo(ano_inicio, ano_fim)
    loc = common.resolver_localidade(localidade)
    _, desmat = common.serie_desmatamento(loc["id"], ano_inicio, ano_fim)
    clima = {
        l["ano"]: (float(l["temperatura_media_c"]), float(l["precipitacao_mm"]))
        for l in query(
            """SELECT ano, temperatura_media_c, precipitacao_mm FROM dado_climatico
               WHERE localidade_id = %s AND temperatura_media_c IS NOT NULL
                 AND precipitacao_mm IS NOT NULL""",
            (loc["id"],),
        )
    }
    # só os anos que têm desmatamento E clima, para as séries serem comparáveis
    pontos = [
        ClimaPonto(ano=ano, area_km2=area, temperatura_media_c=clima[ano][0], precipitacao_mm=clima[ano][1])
        for ano, area in desmat if ano in clima
    ]
    if not pontos:
        raise HTTPException(
            404, f"Não há anos com dados de desmatamento e de clima para {loc['nome']} no período pedido."
        )

    areas = [p.area_km2 for p in pontos]
    temps = [p.temperatura_media_c for p in pontos]
    chuvas = [p.precipitacao_mm for p in pontos]
    texto = common.insight(loc["id"], "CORRELACAO_CLIMATICA")

    return ClimateCorrelationOut(
        serie=pontos,
        indicadores=IndicadoresClimaticos(
            taxa_supressao_pct=taxa_supressao_pct(areas),
            anomalia_termica_c=desvio_da_media(temps),
            deficit_hidrico_mm=desvio_da_media(chuvas),
            coef_correlacao_temperatura=correlacao(areas, temps),
            coef_correlacao_precipitacao=correlacao(areas, chuvas),
        ),
        insight=texto["texto"] if texto else None,
        atualizado_em=common.atualizado_em(),
    )
