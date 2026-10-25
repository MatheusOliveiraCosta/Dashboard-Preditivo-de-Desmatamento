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
import type { SeriePonto } from '@/types/api'

Chart.register(
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler,
  Tooltip,
)

const props = defineProps<{ serie: SeriePonto[] }>()

const canvas = ref<HTMLCanvasElement | null>(null)
let grafico: Chart<'line'> | null = null

const COR_LINHA = '#0a2408'
const COR_PICO = '#93000a'
const COR_TEXTO = '#2c3228'
const FAMILIA = 'Inter, system-ui, sans-serif'

const numero = new Intl.NumberFormat('pt-BR')

// O ano de maior valor é destacado em vermelho (ponto e rótulo do eixo).
const indicePico = computed(() => {
  let pico = 0
  props.serie.forEach((p, i) => {
    if (p.area_km2 > (props.serie[pico]?.area_km2 ?? -Infinity)) pico = i
  })
  return pico
})

const descricao = computed(() => {
  const primeiro = props.serie[0]
  const ultimo = props.serie.at(-1)
  const pico = props.serie[indicePico.value]
  if (!primeiro || !ultimo || !pico) return 'Gráfico sem dados.'
  return `Área desmatada em km² de ${primeiro.ano} a ${ultimo.ano}. O maior valor foi em ${pico.ano}: ${numero.format(pico.area_km2)} km².`
})

function montarDados(): ChartData<'line'> {
  return {
    labels: props.serie.map((p) => String(p.ano)),
    datasets: [
      {
        data: props.serie.map((p) => p.area_km2),
        borderColor: COR_LINHA,
        borderWidth: 5,
        tension: 0,
        fill: true,
        backgroundColor: (contexto) => {
          const { ctx, chartArea } = contexto.chart
          if (!chartArea) return 'rgba(10, 36, 8, 0.2)'
          const degrade = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
          degrade.addColorStop(0, 'rgba(10, 36, 8, 0.38)')
          degrade.addColorStop(1, 'rgba(10, 36, 8, 0.04)')
          return degrade
        },
        pointBackgroundColor: '#ffffff',
        pointBorderWidth: 3,
        pointBorderColor: (c) => (c.dataIndex === indicePico.value ? COR_PICO : COR_LINHA),
        pointRadius: (c) => (c.dataIndex === indicePico.value ? 9 : 7),
        pointHoverRadius: 10,
      },
    ],
  }
}

function formatarEixoY(valor: string | number): string {
  const n = Number(valor)
  return n >= 1000 ? `${n / 1000}k` : String(n)
}

function montarOpcoes(): ChartOptions<'line'> {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    interaction: { mode: 'index', intersect: false },
    layout: { padding: { left: 8, right: 16, top: 16 } },
    plugins: {
      legend: { display: false },
      tooltip: {
        displayColors: false,
        backgroundColor: '#2d312e',
        borderColor: 'rgba(82, 89, 78, 0.3)',
        borderWidth: 1,
        cornerRadius: 12,
        padding: 16,
        caretSize: 8,
        titleColor: '#e0e3df',
        titleFont: { family: FAMILIA, size: 14, weight: 'bold' },
        bodyColor: '#bcf0ae',
        bodyFont: { family: 'Montserrat, Inter, sans-serif', size: 22, weight: 'bold' },
        callbacks: {
          label: (item) => `${numero.format(Number(item.parsed.y))} km²`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grace: '5%',
        // no Chart.js 4, o tracejado das linhas de grade é configurado em border.dash
        border: { display: false, dash: [6, 6] },
        grid: { color: 'rgba(82, 89, 78, 0.45)' },
        ticks: {
          callback: formatarEixoY,
          color: COR_TEXTO,
          font: { family: FAMILIA, size: 16 },
          maxTicksLimit: 5,
        },
      },
      x: {
        border: { display: false },
        grid: { display: false },
        ticks: {
          autoSkip: false,
          maxRotation: 0,
          color: (c) => (c.index === indicePico.value ? COR_PICO : COR_TEXTO),
          font: (c) => ({
            family: FAMILIA,
            size: 16,
            weight: c.index === indicePico.value ? 'bold' : 'normal',
          }),
          // rótulos no formato do Figma: '14, '15 ...
          callback: (_valor, indice) => `'${String(props.serie[indice]?.ano ?? '').slice(-2)}`,
        },
      },
    },
  }
}

onMounted(() => {
  if (!canvas.value) return
  grafico = new Chart(canvas.value, { type: 'line', data: montarDados(), options: montarOpcoes() })
})

watch(
  () => props.serie,
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
