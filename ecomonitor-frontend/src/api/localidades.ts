import localidadesMock from '@/mocks/localidades.json'
import type { Localidade } from '@/types/api'
import { apiGet, USE_MOCK } from './client'

export async function getLocalidades(): Promise<Localidade[]> {
  if (USE_MOCK) return localidadesMock as Localidade[]
  return apiGet<Localidade[]>('/api/v1/localidades')
}
