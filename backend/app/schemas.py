"""modelos de resposta (contrato de api) O fastapi gera o /docs a partir deles"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Localidade(BaseModel):
    codigo: str
    nome: str
    tipo: Literal["estado", "bioma"]
    sigla_uf: str | None = None
    regiao: str | None = None


# ---------- /overview ----------
class Kpi(BaseModel):
    region: str
    area_desmatada_km2: float
    variacao_percentual: float | None  # None se não houver ano anterior
    ano_referencia: int


class PontoSerie(BaseModel):
    ano: int
    area_km2: float


class OverviewResponse(BaseModel):
    kpis: list[Kpi]
    serie_historica: list[PontoSerie]
    insight: str
    atualizado_em: datetime


# ---------- /climate-correlation ----------
class PontoClima(BaseModel):
    ano: int
    area_km2: float
    temperatura_media_c: float
    precipitacao_mm: float


class Correlacao(BaseModel):
    """Coeficiente de Pearson (-1 a 1). None se o período for curto demais."""
    temperatura: float | None
    precipitacao: float | None


class ClimateResponse(BaseModel):
    serie: list[PontoClima]
    correlacao: Correlacao
    insight: str
    atualizado_em: datetime


# ---------- /projection ----------
class PontoProjecao(BaseModel):
    ano: int
    valor_km2: float
    intervalo_inferior: float
    intervalo_superior: float


class ProjectionResponse(BaseModel):
    historico: list[PontoSerie]
    projecao_regional: list[PontoProjecao]
    projecao_nacional: list[PontoProjecao]
    insight: str
    atualizado_em: datetime
