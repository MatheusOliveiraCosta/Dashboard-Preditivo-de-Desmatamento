import climateMock from '@/mocks/climate-correlation.json'
import type { ClimateCorrelationParams, ClimateCorrelationResponse } from '@/types/api'
import { apiGet, USE_MOCK } from './client'

export async function getCorrelacaoClimatica(
  params: ClimateCorrelationParams = {},
): Promise<ClimateCorrelationResponse> {
  // No modo mock a resposta é sempre a mesma, independente do filtro de localidade.
  if (USE_MOCK) return climateMock as ClimateCorrelationResponse
  return apiGet<ClimateCorrelationResponse>('/api/v1/climate-correlation', { ...params })
}
