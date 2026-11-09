"""Formato das respostas da API (contrato v1). O frontend espelha estes tipos em
ecomonitor-frontend/src/types/api.ts. Detalhes em docs/arquitetura-contrato-api.md."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class LocalidadeOut(BaseModel):
    id: int
    nome: str
    sigla_uf: str | None
    tipo: Literal["PAIS", "ESTADO", "BIOMA"]
    regiao: str | None


class Kpi(BaseModel):
    region: str
    area_desmatada_km2: float
    variacao_percentual: float | None
    ano_referencia: int


class SeriePonto(BaseModel):
    ano: int
    area_km2: float


class OverviewOut(BaseModel):
    kpis: list[Kpi]
    bioma_critico: str | None
    serie_historica: list[SeriePonto]
    insight: str | None
    atualizado_em: datetime | None


class ClimaPonto(BaseModel):
    ano: int
    area_km2: float
    temperatura_media_c: float
    precipitacao_mm: float


class IndicadoresClimaticos(BaseModel):
    taxa_supressao_pct: float | None
    anomalia_termica_c: float
    deficit_hidrico_mm: float
    coef_correlacao_temperatura: float | None
    coef_correlacao_precipitacao: float | None


class ClimateCorrelationOut(BaseModel):
    serie: list[ClimaPonto]
    indicadores: IndicadoresClimaticos
    insight: str | None
    atualizado_em: datetime | None


class ProjecaoPonto(BaseModel):
    ano: int
    valor_projetado_km2: float
    intervalo_inferior: float
    intervalo_superior: float


class VisaoProjecao(BaseModel):
    serie_historica: list[SeriePonto]
    projecao: list[ProjecaoPonto]
    ponto_estabilizacao: int | None
    insight: str | None


class ProjectionOut(BaseModel):
    geral: VisaoProjecao
    regional: VisaoProjecao | None
    atualizado_em: datetime | None
