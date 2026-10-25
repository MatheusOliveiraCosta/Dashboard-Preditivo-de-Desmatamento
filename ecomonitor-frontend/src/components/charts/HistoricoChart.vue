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

const descricao = computed(() => {
  const primeiro = props.serie[0]
  const ultimo = props.serie[props.serie.length - 1]
  if (!primeiro || !ultimo) return 'Gráfico sem dados.'
  return `Área desmatada em km² de ${primeiro.ano} a ${ultimo.ano}: de ${primeiro.area_km2.toLocaleString('pt-BR')} para ${ultimo.area_km2.toLocaleString('pt-BR')}.`
})

const FONTE = { family: 'Inter, system-ui, sans-serif', size: 10, weight: 700 } as const

function montarDados() {
  const ultimo = props.serie.length - 1
  return {
    labels: props.serie.map((p) => String(p.ano)),
    datasets: [
      {
        data: props.serie.map((p) => p.area_km2),
        borderColor: '#72796e',
        borderWidth: 1.5,
        tension: 0,
        fill: true,
        backgroundColor: (contexto: { chart: Chart }) => {
          const { ctx, chartArea } = contexto.chart
          if (!chartArea) return 'rgba(114, 121, 110, 0.2)'
          const degrade = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
          degrade.addColorStop(0, 'rgba(114, 121, 110, 0.4)')
          degrade.addColorStop(1, 'rgba(114, 121, 110, 0.02)')
          return degrade
        },
        // só o primeiro e o último ponto ficam marcados, como no Figma
        pointRadius: (contexto: { dataIndex: number }) =>
          contexto.dataIndex === 0 || contexto.dataIndex === ultimo ? 4 : 0,
        pointHoverRadius: 5,
        pointBackgroundColor: '#191c1a',
        pointBorderColor: '#191c1a',
      },
    ],
  }
}

function formatarEixoY(valor: string | number): string {
  const n = Number(valor)
  return n >= 1000 ? `${n / 1000}k` : String(n)
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
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (item) => ` ${Number(item.parsed.y).toLocaleString('pt-BR')} km²`,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          border: { display: false },
          grid: { color: '#c2c9bb' },
          ticks: { callback: formatarEixoY, color: '#191c1a', font: FONTE, maxTicksLimit: 4 },
        },
        x: {
          border: { display: false },
          grid: { display: false },
          ticks: {
            autoSkip: false,
            maxRotation: 0,
            color: '#191c1a',
            font: FONTE,
            // com muitos anos mostra um rótulo a cada 4 e o último; com poucos, todos
            callback(_valor, indice) {
              const total = props.serie.length
              if (total <= 6 || indice % 4 === 0 || indice === total - 1) {
                return props.serie[indice]?.ano
              }
              return ''
            },
          },
        },
      },
    },
  })
}

onMounted(criar)

watch(
  () => props.serie,
  () => {
    if (!grafico) return
    grafico.data = montarDados()
    grafico.update()
  },
  { deep: true },
)

onBeforeUnmount(() => grafico?.destroy())

// Usado futuramente pelo botão "Exportar Gráfico PNG" (RF17).
defineExpose({ exportarPng: () => (grafico ? canvasParaPng(grafico.canvas) : null) })
</script>

<template>
  <canvas ref="canvas" role="img" :aria-label="descricao" />
</template>
