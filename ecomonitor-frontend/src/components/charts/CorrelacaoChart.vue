<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  CategoryScale,
  Chart,
  Filler,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'
import { canvasParaPng } from '@/utils/exportPng'
import type { ClimaPonto } from '@/types/api'

Chart.register(
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler,
  Tooltip,
)

const props = defineProps<{ serie: ClimaPonto[] }>()

const canvas = ref<HTMLCanvasElement | null>(null)
let grafico: Chart<'line'> | null = null

const COR_DESMATAMENTO = '#93000a'
const COR_TEMPERATURA = '#b45309'
const COR_PRECIPITACAO = '#2d5a27'

const numero = new Intl.NumberFormat('pt-BR')
const decimal = new Intl.NumberFormat('pt-BR', {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
})

const descricao = computed(() => {
  const primeiro = props.serie[0]
  const ultimo = props.serie[props.serie.length - 1]
  if (!primeiro || !ultimo) return 'Gráfico sem dados.'
  return `Desmatamento, temperatura média e precipitação de ${primeiro.ano} a ${ultimo.ano}.`
})

// As três grandezas têm unidades diferentes (km², °C e mm), então cada uma usa
// um eixo próprio e invisível, ajustado ao seu intervalo, para as curvas
// ocuparem a mesma altura do gráfico.
function limites(valores: number[]) {
  const min = Math.min(...valores)
  const max = Math.max(...valores)
  const folga = (max - min) * 0.1 || 1
  return { min: min - folga, max: max + folga }
}

function montarDados() {
  return {
    labels: props.serie.map((p) => String(p.ano)),
    datasets: [
      {
        label: 'Desmatamento (km²)',
        data: props.serie.map((p) => p.area_km2),
        yAxisID: 'yDesmatamento',
        order: 1,
        borderColor: COR_DESMATAMENTO,
        borderWidth: 3,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointBackgroundColor: COR_DESMATAMENTO,
      },
      {
        label: 'Temperatura (°C)',
        data: props.serie.map((p) => p.temperatura_media_c),
        yAxisID: 'yTemperatura',
        order: 2,
        borderColor: COR_TEMPERATURA,
        borderWidth: 2,
        borderDash: [6, 4],
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointBackgroundColor: COR_TEMPERATURA,
      },
      {
        label: 'Precipitação (mm)',
        data: props.serie.map((p) => p.precipitacao_mm),
        yAxisID: 'yPrecipitacao',
        order: 3,
        fill: 'start' as const,
        backgroundColor: 'rgba(45, 90, 39, 0.25)',
        borderWidth: 0,
        tension: 0,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointBackgroundColor: COR_PRECIPITACAO,
      },
    ],
  }
}

function montarEscalas() {
  const d = limites(props.serie.map((p) => p.area_km2))
  const t = limites(props.serie.map((p) => p.temperatura_media_c))
  const p = limites(props.serie.map((x) => x.precipitacao_mm))
  return {
    x: {
      border: { display: false },
      grid: { display: false },
      ticks: {
        autoSkip: false,
        maxRotation: 0,
        color: '#2b3028',
        font: { family: 'Inter, system-ui, sans-serif', size: 16 },
        // um rótulo a cada 2 anos, mais o último
        callback(_valor: string | number, indice: number) {
          const ultimo = props.serie.length - 1
          return indice % 2 === 0 || indice === ultimo ? props.serie[indice]?.ano : ''
        },
      },
    },
    yDesmatamento: {
      position: 'left' as const,
      min: d.min,
      max: d.max,
      // no Chart.js 4, o tracejado das linhas de grade é configurado em border.dash
      border: { display: false, dash: [4, 4] },
      grid: { color: 'rgba(144, 150, 140, 0.35)' },
      ticks: { display: false, count: 5 },
    },
    yTemperatura: { display: false, min: t.min, max: t.max },
    yPrecipitacao: { display: false, min: p.min, max: p.max },
  }
}

function criar() {
  if (!canvas.value) return
  grafico = new Chart(canvas.value, {
    type: 'line',
    data: montarDados(),
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false }, // a legenda é o componente LegendaGrafico
        tooltip: {
          callbacks: {
            label(item) {
              const y = Number(item.parsed.y)
              const rotulo = item.dataset.label ?? ''
              if (rotulo.startsWith('Temperatura')) return ` ${rotulo}: ${decimal.format(y)} °C`
              if (rotulo.startsWith('Precipitação')) return ` ${rotulo}: ${numero.format(y)} mm`
              return ` ${rotulo}: ${numero.format(y)} km²`
            },
          },
        },
      },
      scales: montarEscalas(),
    },
  })
}

onMounted(criar)

watch(
  () => props.serie,
  () => {
    if (!grafico) return
    grafico.data = montarDados()
    grafico.options.scales = montarEscalas()
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
