// Interfaces espelhando o contrato da API (v1). Ajuste aqui se o contrato mudar.

export type TipoLocalidade = 'ESTADO' | 'BIOMA'

export interface Localidade {
  id: number
  nome: string
  sigla_uf: string | null
  tipo: TipoLocalidade
  regiao: string | null
}

export interface Kpi {
  region: string
  area_desmatada_km2: number
  variacao_percentual: number
  ano_referencia: number
}

export interface SeriePonto {
  ano: number
  area_km2: number
}

export interface OverviewParams {
  localidade?: number | null // ausente/null = Brasil
  ano_inicio?: number
  ano_fim?: number
}

export interface OverviewResponse {
  kpis: Kpi[]
  // PENDENTE NO CONTRATO: o card "Bioma crítico" (RF06) precisa deste campo,
  // que ainda não consta em /api/v1/overview.
  bioma_critico: string
  serie_historica: SeriePonto[]
  insight: string
  atualizado_em: string
}

// ---- /api/v1/climate-correlation ----

export interface ClimateCorrelationParams {
  localidade?: number | null // ausente/null = Brasil
  start?: number
  end?: number
}

export interface ClimaPonto {
  ano: number
  area_km2: number
  temperatura_media_c: number
  precipitacao_mm: number
}

// PENDENTE NO CONTRATO: os 3 cards da tela (RF08) precisam destes indicadores,
// que ainda não constam na resposta de /api/v1/climate-correlation.
export interface IndicadoresClimaticos {
  taxa_supressao_pct: number
  anomalia_termica_c: number
  deficit_hidrico_mm: number
  coef_correlacao_temperatura: number
  coef_correlacao_precipitacao: number
}

export interface ClimateCorrelationResponse {
  serie: ClimaPonto[]
  indicadores: IndicadoresClimaticos
  insight: string
  atualizado_em: string
}

// ---- /api/v1/projection ----

export interface ProjectionParams {
  localidade?: number | null // ausente/null = só a visão Geral (Brasil)
  horizon?: number
}

export interface ProjecaoPonto {
  ano: number
  valor_projetado_km2: number
  intervalo_inferior: number
  intervalo_superior: number
}

export interface VisaoProjecao {
  serie_historica: SeriePonto[]
  projecao: ProjecaoPonto[]
  // PENDENTE: critério do "Ponto de Estabilização". No mock, é o primeiro ano projetado
  // com variação anual menor que 1% (em módulo). Definir com a equipe de Dados/IA.
  ponto_estabilizacao: number | null
  insight: string
}

// PENDENTE NO CONTRATO: o Figma alterna entre Geral e Regional, e cada visão precisa do
// próprio histórico, projeção e texto. O contrato atual traz só uma `serie_historica`.
export interface ProjectionResponse {
  geral: VisaoProjecao
  regional: VisaoProjecao | null // null quando nenhuma localidade está selecionada
  atualizado_em: string
}
