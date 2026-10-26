from fastapi import APIRouter, Query

from app import mock_data
from app.mock_data import ANO_MAX, ANO_MIN
from app.routers.common import resolver_localidade, validar_periodo
from app.schemas import OverviewResponse

router = APIRouter()


@router.get("/overview", response_model=OverviewResponse)
def overview(
    localidade: str | None = Query(None, description="UF ou slug do bioma. Ausente = Brasil."),
    ano_inicio: int = Query(ANO_MIN, ge=ANO_MIN, le=ANO_MAX),
    ano_fim: int = Query(ANO_MAX, ge=ANO_MIN, le=ANO_MAX),
):
    codigo = resolver_localidade(localidade)
    validar_periodo(ano_inicio, ano_fim)
    serie = mock_data.serie_desmatamento(codigo, ano_inicio, ano_fim)
    return {
        "kpis": mock_data.kpis(codigo),
        "serie_historica": serie,
        "insight": mock_data.insight_overview(codigo, serie),
        "atualizado_em": mock_data.ATUALIZADO_EM,
    }
