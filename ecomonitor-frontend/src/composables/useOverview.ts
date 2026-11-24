
import { computed, ref, watch } from 'vue'
import { getOverview } from '@/api/overview'
import { useFiltrosStore } from '@/stores/filtros'
import type { OverviewResponse } from '@/types/api'

export function useOverview() {
  const filtros = useFiltrosStore()

  const dados = ref<OverviewResponse | null>(null)
  const carregando = ref(false)
  const erro = ref<string | null>(null)

  // Impede que respostas antigas substituam dados novos.
  let idRequisicao = 0

  async function carregar() {
    const idAtual = ++idRequisicao
    const localidade = filtros.localidadeId

    carregando.value = true
    erro.value = null

    // Remove os dados da localidade anterior.
    dados.value = null

    try {
      const resposta = await getOverview({ localidade })

      if (idAtual !== idRequisicao) return

      dados.value = resposta

    } catch (e) {
      if (idAtual !== idRequisicao) return

      dados.value = null

      erro.value =
        e instanceof Error
          ? e.message
          : 'Não foi possível carregar os dados.'

    } finally {
      if (idAtual === idRequisicao) {
        carregando.value = false
      }
    }
  }

  // Atualiza quando o estado ou bioma mudar.
  watch(
    () => filtros.localidadeId,
    carregar,
    { immediate: true }
  )

  const kpi = computed(() => dados.value?.kpis[0] ?? null)

  const serie = computed(() => {
    const completa = dados.value?.serie_historica ?? []

    const quantidade =
      filtros.periodo === '1ano'
        ? 1
        : filtros.periodo === '5anos'
          ? 5
          : completa.length

    return completa.slice(-quantidade)
  })

  return {
    dados,
    kpi,
    serie,
    carregando,
    erro,
    recarregar: carregar
  }
}
