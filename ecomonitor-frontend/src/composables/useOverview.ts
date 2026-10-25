import { computed, ref, watch } from 'vue'
import { getOverview } from '@/api/overview'
import { useFiltrosStore } from '@/stores/filtros'
import type { OverviewResponse } from '@/types/api'

export function useOverview() {
  const filtros = useFiltrosStore()
  const dados = ref<OverviewResponse | null>(null)
  const carregando = ref(false)
  const erro = ref<string | null>(null)

  async function carregar() {
    carregando.value = true
    erro.value = null
    try {
      dados.value = await getOverview({ localidade: filtros.localidadeId })
    } catch (e) {
      erro.value = e instanceof Error ? e.message : 'Não foi possível carregar os dados.'
    } finally {
      carregando.value = false
    }
  }

  watch(() => filtros.localidadeId, carregar, { immediate: true })

  const kpi = computed(() => dados.value?.kpis[0] ?? null)

  // Aplica o filtro de período (RF05) sobre a série anual.
  const serie = computed(() => {
    const completa = dados.value?.serie_historica ?? []
    const quantidade =
      filtros.periodo === '1ano' ? 1 : filtros.periodo === '5anos' ? 5 : completa.length
    return completa.slice(-quantidade)
  })

  return { dados, kpi, serie, carregando, erro, recarregar: carregar }
}
