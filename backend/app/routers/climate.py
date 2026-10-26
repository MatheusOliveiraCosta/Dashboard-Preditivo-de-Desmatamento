from fastapi import APIRouter, Query

from app import mock_data
from app.mock_data import ANO_MAX, ANO_MIN
from app.routers.common import resolver_localidade, validar_periodo
from app.schemas import ClimateResponse

router = APIRouter()


@router.get("/climate-correlation", response_model=ClimateResponse)
def climate_correlation(
    localidade: str | None = Query(None, description="UF ou slug do bioma. Ausente = Brasil."),
    start: int = Query(ANO_MIN, ge=ANO_MIN, le=ANO_MAX),
    end: int = Query(ANO_MAX, ge=ANO_MIN, le=ANO_MAX),
):
    codigo = resolver_localidade(localidade)
    validar_periodo(start, end)
    serie = mock_data.serie_clima(codigo, start, end)
    areas = [p["area_km2"] for p in serie]
    r_temp = mock_data.pearson(areas, [p["temperatura_media_c"] for p in serie])
    r_prec = mock_data.pearson(areas, [p["precipitacao_mm"] for p in serie])
    return {
        "serie": serie,
        "correlacao": {"temperatura": r_temp, "precipitacao": r_prec},
        "insight": mock_data.insight_clima(codigo, start, end, r_temp),
        "atualizado_em": mock_data.ATUALIZADO_EM,
    }
