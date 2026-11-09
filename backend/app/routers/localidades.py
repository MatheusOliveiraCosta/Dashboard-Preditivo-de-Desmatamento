from fastapi import APIRouter

from app.db import query
from app.schemas import LocalidadeOut

router = APIRouter()


@router.get("/localidades", response_model=list[LocalidadeOut], tags=["localidades"])
def listar_localidades():
    """Brasil, estados e biomas. Popula os filtros do frontend."""
    return query(
        """SELECT id, nome, sigla_uf, tipo, regiao FROM localidade
           ORDER BY CASE tipo WHEN 'PAIS' THEN 0 WHEN 'ESTADO' THEN 1 ELSE 2 END, nome"""
    )
