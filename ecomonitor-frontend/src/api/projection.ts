import projectionMock from '@/mocks/projection.json'
import type { ProjectionParams, ProjectionResponse } from '@/types/api'
import { apiGet, USE_MOCK } from './client'

export async function getProjecao(params: ProjectionParams = {}): Promise<ProjectionResponse> {
  if (USE_MOCK) {
    // Imita a API: a visão regional só existe quando há uma localidade selecionada.
    const mock = projectionMock as ProjectionResponse
    return { ...mock, regional: params.localidade ? mock.regional : null }
  }
  return apiGet<ProjectionResponse>('/api/v1/projection', { ...params })
}
