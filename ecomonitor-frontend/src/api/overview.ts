import overviewMock from '@/mocks/overview.json'
import type { OverviewParams, OverviewResponse } from '@/types/api'
import { apiGet, USE_MOCK } from './client'

export async function getOverview(params: OverviewParams = {}): Promise<OverviewResponse> {
  // No modo mock a resposta é sempre a mesma, independente do filtro de localidade.
  if (USE_MOCK) return overviewMock as OverviewResponse
  return apiGet<OverviewResponse>('/api/v1/overview', { ...params })
}
