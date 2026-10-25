import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export type Periodo = '1ano' | '5anos' | 'historico'

// Filtros compartilhados entre as telas (RF04 e RF05).
export const useFiltrosStore = defineStore('filtros', () => {
  const estadoId = ref<number | null>(null)
  const biomaId = ref<number | null>(null)
  const periodo = ref<Periodo>('historico')

  // O modelo de dados tem uma única dimensão "localidade" (estado OU bioma),
  // por isso escolher um limpa o outro. null = Brasil.
  const localidadeId = computed(() => estadoId.value ?? biomaId.value)

  function selecionarEstado(id: number | null) {
    estadoId.value = id
    if (id !== null) biomaId.value = null
  }

  function selecionarBioma(id: number | null) {
    biomaId.value = id
    if (id !== null) estadoId.value = null
  }

  // Clicar no período ativo volta para o histórico completo.
  function alternarPeriodo(novo: '1ano' | '5anos') {
    periodo.value = periodo.value === novo ? 'historico' : novo
  }

  return {
    estadoId,
    biomaId,
    periodo,
    localidadeId,
    selecionarEstado,
    selecionarBioma,
    alternarPeriodo,
  }
})
