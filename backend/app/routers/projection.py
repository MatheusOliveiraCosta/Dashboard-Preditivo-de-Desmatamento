from fastapi import APIRouter, Query

from app import mock_data
from app.mock_data import ANO_MAX, ANO_MIN
from app.routers.common import resolver_localidade
from app.schemas import ProjectionResponse

router = APIRouter()


@router.get("/projection", response_model=ProjectionResponse)
def projection(
    localidade: str | None = Query(None, description="UF ou slug do bioma. Ausente = Brasil."),
    horizon: int = Query(5, ge=1, le=10, description="Anos à frente a projetar."),
):
    codigo = resolver_localidade(localidade)
    regional = mock_data.projetar(codigo, horizon)
    nacional = mock_data.projetar(None, horizon)  # sem localidade, regional == nacional
    return {
        "historico": mock_data.serie_desmatamento(codigo, ANO_MIN, ANO_MAX),
        "projecao_regional": regional,
        "projecao_nacional": nacional,
        "insight": mock_data.insight_projecao(codigo, regional),
        "atualizado_em": mock_data.ATUALIZADO_EM,
    }
