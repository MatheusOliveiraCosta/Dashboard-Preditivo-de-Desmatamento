import type { ChartType, Plugin } from 'chart.js'

export interface MarcadoresOpcoes {
  // posição (categoria) do último ano observado: ali fica a linha pontilhada
  indiceBase: number
  // anotação "Ponto de Estabilização"; null/ausente = não desenha
  estabilizacao?: { indice: number; valor: number; ano: number } | null
}

declare module 'chart.js' {
  interface PluginOptionsByType<TType extends ChartType> {
    marcadoresProjecao?: MarcadoresOpcoes
  }
}

const FONTE = 'Inter, system-ui, sans-serif'

// Desenha a linha pontilhada que separa histórico de projeção e a anotação
// do ponto de estabilização, como no Figma.
export const marcadoresProjecao: Plugin<'line'> = {
  id: 'marcadoresProjecao',

  beforeDatasetsDraw(chart, _args, opcoes) {
    const x = chart.scales.x
    if (!opcoes || !x) return
    const { ctx, chartArea } = chart
    const xBase = x.getPixelForValue(opcoes.indiceBase)
    ctx.save()
    ctx.setLineDash([2, 3])
    ctx.strokeStyle = '#6b7466'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(xBase, chartArea.top)
    ctx.lineTo(xBase, chartArea.bottom)
    ctx.stroke()
    ctx.restore()
  },

  afterDatasetsDraw(chart, _args, opcoes) {
    const x = chart.scales.x
    const y = chart.scales.y
    const est = opcoes?.estabilizacao
    if (!x || !y || !est) return
    const { ctx, chartArea } = chart

    const px = x.getPixelForValue(est.indice)
    const py = y.getPixelForValue(est.valor)

    // largura da caixa ajustada ao texto (a fonte pode variar de um computador para outro)
    const linha1 = 'Ponto de Estabilização'
    const linha2 = `Previsto para ${est.ano}`
    ctx.save()
    ctx.font = `700 13px ${FONTE}`
    const largura1 = ctx.measureText(linha1).width
    ctx.font = `700 12px ${FONTE}`
    const largura2 = ctx.measureText(linha2).width
    ctx.restore()
    const largura = Math.ceil(Math.max(largura1, largura2)) + 20
    const altura = 46
    const boxX = Math.min(Math.max(px - 30, chartArea.left + 4), chartArea.right - largura - 4)
    const boxY = Math.max(py - 96, chartArea.top + 4)

    ctx.save()

    // linha-guia pontilhada até o ponto
    ctx.setLineDash([2, 3])
    ctx.strokeStyle = '#6b7466'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(px, boxY + altura)
    ctx.lineTo(px, py - 6)
    ctx.stroke()
    ctx.setLineDash([])

    // marcador no ponto
    ctx.fillStyle = '#ffffff'
    ctx.strokeStyle = '#0a2608'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(px, py, 5, 0, Math.PI * 2)
    ctx.fill()
    ctx.stroke()

    // caixa
    ctx.fillStyle = 'rgba(225, 228, 223, 0.95)'
    ctx.beginPath()
    ctx.roundRect(boxX, boxY, largura, altura, 6)
    ctx.fill()

    ctx.textBaseline = 'top'
    ctx.fillStyle = '#111412'
    ctx.font = `700 13px ${FONTE}`
    ctx.fillText(linha1, boxX + 10, boxY + 9)
    ctx.fillStyle = '#2b3328'
    ctx.font = `700 12px ${FONTE}`
    ctx.fillText(linha2, boxX + 10, boxY + 27)

    ctx.restore()
  },
}
