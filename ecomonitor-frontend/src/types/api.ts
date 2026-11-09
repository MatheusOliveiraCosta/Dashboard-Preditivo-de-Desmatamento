// Interfaces espelhando o contrato da API (v1). Ajuste aqui se o contrato mudar.

// PAIS é o registro "Brasil" (aparece em /localidades; os filtros mostram só ESTADO e BIOMA)
export type TipoLocalidade = 'PAIS' | 'ESTADO' | 'BIOMA'

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
  variacao_percentual: number | null // null se não houver ano anterior para comparar
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
  bioma_critico: string | null // bioma com a maior área desmatada no ano de referência (RF06)
  serie_historica: SeriePonto[]
  insight: string | null // texto gerado pelo ETL (RF18); null se ainda não foi gerado
  atualizado_em: string | null // última atualização bem-sucedida dos dados (UTC)
}

// ---- /api/v1/climate-correlation ----

export interface ClimateCorrelationParams {
  localidade?: number | null // ausente/null = Brasil
  ano_inicio?: number
  ano_fim?: number
}

export interface ClimaPonto {
  ano: number
  area_km2: number
  temperatura_media_c: number
  precipitacao_mm: number
}

// Indicadores dos 3 cards da tela (RF08), calculados pela API para o período devolvido.
export interface IndicadoresClimaticos {
  taxa_supressao_pct: number | null
  anomalia_termica_c: number
  deficit_hidrico_mm: number
  coef_correlacao_temperatura: number | null // null com menos de 3 anos ou série constante
  coef_correlacao_precipitacao: number | null
}

export interface ClimateCorrelationResponse {
  serie: ClimaPonto[]
  indicadores: IndicadoresClimaticos
  insight: string | null
  atualizado_em: string | null
}

// ---- /api/v1/projection ----

export interface ProjectionParams {
  localidade?: number | null // ausente/null = só a visão Geral (Brasil)
  horizonte?: number // anos à frente (padrão: todos os calculados)
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
  // PROVISÓRIO: primeiro ano projetado com variação anual menor que 1% (em módulo).
  // O critério ainda precisa ser validado com a equipe de Dados/IA.
  ponto_estabilizacao: number | null
  insight: string | null
}

// Cada visão (Geral = Brasil, Regional = localidade escolhida) traz o próprio histórico,
// projeção e texto, porque o Figma alterna entre as duas.
export interface ProjectionResponse {
  geral: VisaoProjecao
  regional: VisaoProjecao | null // null quando nenhuma localidade está selecionada
  atualizado_em: string | null
}
