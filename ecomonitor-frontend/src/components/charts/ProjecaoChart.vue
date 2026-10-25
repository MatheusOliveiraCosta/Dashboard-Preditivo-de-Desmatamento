<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  CategoryScale,
  Chart,
  type ChartData,
  type ChartOptions,
  Filler,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'
import { canvasParaPng } from '@/utils/exportPng'
import type { VisaoProjecao } from '@/types/api'
import { marcadoresProjecao } from './plugins/marcadoresProjecao'

Chart.register(
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler,
  Tooltip,
  marcadoresProjecao,
)

const props = defineProps<{ visao: VisaoProjecao }>()

const canvas = ref<HTMLCanvasElement | null>(null)
let grafico: Chart<'line'> | null = null

const COR_LINHA = '#0a2608'
const COR_MARGEM = 'rgba(214, 122, 58, 0.6)'

const numero = new Intl.NumberFormat('pt-BR')

// Eixo X contínuo: anos observados seguidos dos anos projetados.
const anos = computed(() => [
  ...props.visao.serie_historica.map((p) => p.ano),
  ...props.visao.projecao.map((p) => p.ano),
])
const indiceBase = computed(() => props.visao.serie_historica.length - 1)

const descricao = computed(() => {
  const h = props.visao.serie_historica
  const p = props.visao.projecao
  if (!h.length || !p.length) return 'Gráfico sem dados.'
  return `Área desmatada em km²: observada de ${h[0]?.ano} a ${h.at(-1)?.ano} e projetada de ${p[0]?.ano} a ${p.at(-1)?.ano}, com margem de incerteza.`
})

function montarDados(): ChartData<'line'> {
  const h = props.visao.serie_historica
  const p = props.visao.projecao
  const base = h.at(-1)?.area_km2 ?? null
  const vazioHistorico = h.slice(0, -1).map(() => null)

  // A projeção e a margem começam exatamente no último valor observado.
  const comecando = (valores: number[]) => [...vazioHistorico, base, ...valores]
  const historico = [...h.map((x) => x.area_km2), ...p.map(() => null)]

  return {
    labels: anos.value.map(String),
    datasets: [
      {
        label: 'margem-inferior',
        data: comecando(p.map((x) => x.intervalo_inferior)),
        order: 10,
        borderWidth: 0,
        pointRadius: 0,
        pointHoverRadius: 0,
        fill: false,
        tension: 0,
      },
      {
        label: 'margem-superior',
        data: comecando(p.map((x) => x.intervalo_superior)),
        order: 11,
        borderWidth: 0,
        pointRadius: 0,
        pointHoverRadius: 0,
        fill: '-1',
        backgroundColor: COR_MARGEM,
        tension: 0,
      },
      {
        label: 'Projeção',
        data: comecando(p.map((x) => x.valor_projetado_km2)),
        order: 2,
        borderColor: COR_LINHA,
        borderWidth: 2.5,
        borderDash: [6, 5],
        pointStyle: 'rectRot' as const,
        pointRadius: (c: { dataIndex: number }) => (c.dataIndex === indiceBase.value ? 0 : 4),
        pointBackgroundColor: COR_LINHA,
        pointBorderColor: COR_LINHA,
        tension: 0,
        spanGaps: false,
        fill: false,
      },
      {
        label: 'Histórico',
        data: historico,
        order: 1,
        borderColor: COR_LINHA,
        borderWidth: 3,
        pointStyle: 'rectRot' as const,
        pointRadius: (c: { dataIndex: number }) => (c.dataIndex === indiceBase.value ? 6 : 4),
        pointBackgroundColor: COR_LINHA,
        pointBorderColor: COR_LINHA,
        tension: 0,
        spanGaps: false,
        fill: false,
      },
    ],
  }
}

function formatarEixoY(valor: string | number): string {
  const n = Number(valor)
  return n >= 1000
    ? `${new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format(n / 1000)}k`
    : String(n)
}

function opcoesDoPlugin() {
  const est = props.visao.ponto_estabilizacao
  const indice = est === null ? -1 : anos.value.indexOf(est)
  const ponto = indice >= 0 ? props.visao.projecao.find((x) => x.ano === est) : undefined
  return {
    indiceBase: indiceBase.value,
    estabilizacao:
      est !== null && ponto ? { indice, valor: ponto.valor_projetado_km2, ano: est } : null,
  }
}

function montarOpcoes(): ChartOptions<'line'> {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    interaction: { mode: 'index' as const, intersect: false },
    layout: { padding: { right: 8 } },
    plugins: {
      legend: { display: false }, // a legenda é o componente LegendaGrafico
      marcadoresProjecao: opcoesDoPlugin(),
      tooltip: {
        filter: (item: { dataset: { label?: string } }) =>
          item.dataset.label === 'Histórico' || item.dataset.label === 'Projeção',
        callbacks: {
          label: (item: { dataset: { label?: string }; parsed: { y: number | null } }) =>
            ` ${item.dataset.label}: ${numero.format(Number(item.parsed.y))} km²`,
          afterBody(itens: { dataset: { label?: string }; dataIndex: number }[]) {
            const item = itens.find((i) => i.dataset.label === 'Projeção')
            if (!item) return ''
            const ponto = props.visao.projecao[item.dataIndex - props.visao.serie_historica.length]
            return ponto
              ? ` Margem: ${numero.format(ponto.intervalo_inferior)} a ${numero.format(ponto.intervalo_superior)} km²`
              : ''
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grace: '5%',
        // no Chart.js 4, o tracejado das linhas de grade é configurado em border.dash
        border: { display: false, dash: [4, 4] },
        grid: { color: 'rgba(194, 201, 187, 0.7)' },
        ticks: {
          callback: formatarEixoY,
          color: '#111412',
          font: { family: 'Inter, system-ui, sans-serif', size: 14 },
          maxTicksLimit: 5,
        },
      },
      x: {
        border: { display: false },
        grid: { display: false },
        ticks: {
          autoSkip: false,
          maxRotation: 0,
          font: { family: 'Inter, system-ui, sans-serif', size: 14 },
          // o ano base fica destacado em verde escuro
          color: (c: { index: number }) => (c.index === indiceBase.value ? COR_LINHA : '#111412'),
          // anos observados: todos; anos projetados: um a cada 2
          callback(_valor: string | number, indice: number) {
            if (indice <= indiceBase.value) return anos.value[indice]
            const ano = anos.value[indice]
            return ano !== undefined && ano % 2 === 0 ? ano : ''
          },
        },
      },
    },
  }
}

function criar() {
  if (!canvas.value) return
  grafico = new Chart(canvas.value, {
    type: 'line',
    data: montarDados(),
    options: montarOpcoes(),
  })
}

onMounted(criar)

watch(
  () => props.visao,
  () => {
    if (!grafico) return
    grafico.data = montarDados()
    grafico.options = montarOpcoes()
    grafico.update()
  },
  { deep: true },
)

onBeforeUnmount(() => grafico?.destroy())

defineExpose({ exportarPng: () => (grafico ? canvasParaPng(grafico.canvas) : null) })
</script>

<template>
  <canvas ref="canvas" role="img" :aria-label="descricao" />
</template>
