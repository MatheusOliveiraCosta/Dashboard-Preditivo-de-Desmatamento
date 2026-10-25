import { computed, ref, watch } from 'vue'
import { getProjecao } from '@/api/projection'
import { useFiltrosStore } from '@/stores/filtros'
import type { ProjectionResponse } from '@/types/api'

export type TipoVisao = 'geral' | 'regional'

export function useProjecaoTendencia() {
  const filtros = useFiltrosStore()
  const dados = ref<ProjectionResponse | null>(null)
  const carregando = ref(false)
  const erro = ref<string | null>(null)
  const tipoVisao = ref<TipoVisao>('geral')

  async function carregar() {
    carregando.value = true
    erro.value = null
    try {
      dados.value = await getProjecao({ localidade: filtros.localidadeId })
    } catch (e) {
      erro.value = e instanceof Error ? e.message : 'Não foi possível carregar os dados.'
    } finally {
      carregando.value = false
    }
  }

  watch(() => filtros.localidadeId, carregar, { immediate: true })

  const regionalDisponivel = computed(() => dados.value?.regional != null)

  // Se a visão regional deixar de existir (filtro limpo), volta para a geral.
  watch(regionalDisponivel, (disponivel) => {
    if (!disponivel) tipoVisao.value = 'geral'
  })

  const visao = computed(() => {
    if (!dados.value) return null
    return tipoVisao.value === 'regional' && dados.value.regional
      ? dados.value.regional
      : dados.value.geral
  })

  const base = computed(() => visao.value?.serie_historica.at(-1) ?? null)
  const final = computed(() => visao.value?.projecao.at(-1) ?? null)
  const primeiroAnoProjetado = computed(() => visao.value?.projecao[0]?.ano)

  return {
    dados,
    visao,
    tipoVisao,
    regionalDisponivel,
    base,
    final,
    primeiroAnoProjetado,
    carregando,
    erro,
    recarregar: carregar,
  }
}
