import { computed, ref } from 'vue'
import { useOverview } from '@/composables/useOverview'
import { useProjecaoTendencia } from '@/composables/useProjecaoTendencia'

// Quantos anos o gráfico "Evolução do Desmatamento" mostra (no Figma: '14 a '24).
export const ANOS_NA_APRESENTACAO = 10

export type IdSlide = 'evolucao' | 'projecao'

export function useApresentacao() {
  const overview = useOverview()
  const projecao = useProjecaoTendencia()

  // O Modo Apresentação ignora o filtro de período e mostra sempre os últimos anos.
  const serieEvolucao = computed(
    () => overview.dados.value?.serie_historica.slice(-ANOS_NA_APRESENTACAO) ?? [],
  )
  const totalAcumulado = computed(() =>
    serieEvolucao.value.reduce((soma, ponto) => soma + ponto.area_km2, 0),
  )

  // Com uma localidade selecionada, mostra a projeção regional; senão, a geral.
  const visaoProjecao = computed(
    () => projecao.dados.value?.regional ?? projecao.dados.value?.geral ?? null,
  )
  const valorFinalProjecao = computed(() => visaoProjecao.value?.projecao.at(-1) ?? null)

  const slides: { id: IdSlide; titulo: [string, string] }[] = [
    { id: 'evolucao', titulo: ['Evolução do', 'Desmatamento'] },
    { id: 'projecao', titulo: ['Projeção do', 'Desmatamento'] },
  ]
  const indice = ref(0)
  const slide = computed(() => slides[indice.value] ?? slides[0]!)

  function proximo() {
    indice.value = (indice.value + 1) % slides.length
  }
  function anterior() {
    indice.value = (indice.value - 1 + slides.length) % slides.length
  }

  return {
    slides,
    indice,
    slide,
    proximo,
    anterior,
    serieEvolucao,
    totalAcumulado,
    visaoProjecao,
    valorFinalProjecao,
    erro: computed(() => overview.erro.value ?? projecao.erro.value),
  }
}
