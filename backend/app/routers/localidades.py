from fastapi import APIRouter

from app import mock_data
from app.schemas import Localidade

router = APIRouter()


@router.get("/localidades", response_model=list[Localidade])
def localidades():
    """Lista de estados e biomas para o filtro."""
    return mock_data.listar_localidades()
