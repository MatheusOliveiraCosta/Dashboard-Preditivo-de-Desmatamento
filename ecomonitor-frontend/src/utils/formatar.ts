const compacto = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 })

// 88208 -> "88,2k"; valores abaixo de mil ficam como estão.
export function formatarCompacto(valor: number): string {
  return Math.abs(valor) >= 1000 ? `${compacto.format(valor / 1000)}k` : compacto.format(valor)
}
