
import { computed, ref, watch } from 'vue'
import { getCorrelacaoClimatica } from '@/api/climate'
import { useFiltrosStore } from '@/stores/filtros'
import type { ClimateCorrelationResponse } from '@/types/api'

export function useCorrelacaoClimatica() {
  const filtros = useFiltrosStore()

  const dados = ref<ClimateCorrelationResponse | null>(null)
  const carregando = ref(false)
  const erro = ref<string | null>(null)

  // Identifica a requisição mais recente.
  // Evita que respostas antigas sobrescrevam filtros novos.
  let idRequisicao = 0

  async function carregar() {
    const idAtual = ++idRequisicao

    // Guarda os filtros utilizados nesta requisição.
    const localidade = filtros.localidadeId
    const periodo = filtros.periodo

    carregando.value = true
    erro.value = null

    try {
      // Busca a série completa para descobrir o último ano
      // disponível na localidade selecionada.
      const respostaCompleta = await getCorrelacaoClimatica({
        localidade,
      })

      if (idAtual !== idRequisicao) return

      // Histórico completo ou ausência de dados.
      if (
        periodo === 'historico' ||
        respostaCompleta.serie.length === 0
      ) {
        dados.value = respostaCompleta
        return
      }

      // Obtém o ano mais recente existente na série.
      const ultimoAno = Math.max(
        ...respostaCompleta.serie.map((ponto) => ponto.ano)
      )

      // Determina a quantidade de anos selecionada.
      const quantidadeAnos = periodo === '1ano' ? 1 : 5

      const anoInicio = ultimoAno - quantidadeAnos + 1

      // Solicita os dados filtrados ao backend.
      // A API também recalcula os indicadores do período.
      const respostaFiltrada = await getCorrelacaoClimatica({
        localidade,
        ano_inicio: anoInicio,
        ano_fim: ultimoAno,
      })

      if (idAtual !== idRequisicao) return

      dados.value = respostaFiltrada

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

  // Atualiza quando a localidade OU o período mudar.
  watch(
    () => [filtros.localidadeId, filtros.periodo],
    carregar,
    { immediate: true }
  )

  // Dados utilizados pelos gráficos e indicadores.
  const serie = computed(() => dados.value?.serie ?? [])

  const anoInicial = computed(() => serie.value[0]?.ano)

  const anoFinal = computed(
    () => serie.value[serie.value.length - 1]?.ano
  )

  return {
    dados,
    serie,
    anoInicial,
    anoFinal,
    carregando,
    erro,
    recarregar: carregar,
  }
}
