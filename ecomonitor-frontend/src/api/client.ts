// Cliente HTTP mínimo. A URL base vem de VITE_API_URL (ver .env.example).
const BASE_URL: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

// Enquanto o backend não existe, as telas usam os JSON de src/mocks.
// Para consumir a API real, defina VITE_USE_MOCK=false no .env.
export const USE_MOCK: boolean = import.meta.env.VITE_USE_MOCK !== 'false'

export async function apiGet<T>(path: string, params: Record<string, unknown> = {}): Promise<T> {
  const url = new URL(path, BASE_URL)
  for (const [chave, valor] of Object.entries(params)) {
    if (valor !== undefined && valor !== null) url.searchParams.set(chave, String(valor))
  }
  const resposta = await fetch(url)
  if (!resposta.ok) throw new Error(`Falha ao consultar ${path} (HTTP ${resposta.status})`)
  return (await resposta.json()) as T
}
