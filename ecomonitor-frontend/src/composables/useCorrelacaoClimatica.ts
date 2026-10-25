import { computed, ref, watch } from 'vue'
import { getCorrelacaoClimatica } from '@/api/climate'
import { useFiltrosStore } from '@/stores/filtros'
import type { ClimateCorrelationResponse } from '@/types/api'

export function useCorrelacaoClimatica() {
  const filtros = useFiltrosStore()
  const dados = ref<ClimateCorrelationResponse | null>(null)
  const carregando = ref(false)
  const erro = ref<string | null>(null)

  async function carregar() {
    carregando.value = true
    erro.value = null
    try {
      dados.value = await getCorrelacaoClimatica({ localidade: filtros.localidadeId })
    } catch (e) {
      erro.value = e instanceof Error ? e.message : 'Não foi possível carregar os dados.'
    } finally {
      carregando.value = false
    }
  }

  watch(() => filtros.localidadeId, carregar, { immediate: true })

  const serie = computed(() => dados.value?.serie ?? [])
  const anoInicial = computed(() => serie.value[0]?.ano)
  const anoFinal = computed(() => serie.value[serie.value.length - 1]?.ano)

  return { dados, serie, anoInicial, anoFinal, carregando, erro, recarregar: carregar }
}
