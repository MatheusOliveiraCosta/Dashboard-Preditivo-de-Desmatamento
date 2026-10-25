// Exportação do gráfico como imagem (RF17), feita no navegador.

// O canvas do gráfico é transparente; aqui ele é copiado para um canvas com fundo branco.
export function canvasParaPng(canvas: HTMLCanvasElement, fundo = '#ffffff'): string | null {
  const copia = document.createElement('canvas')
  copia.width = canvas.width
  copia.height = canvas.height
  const ctx = copia.getContext('2d')
  if (!ctx) return null
  ctx.fillStyle = fundo
  ctx.fillRect(0, 0, copia.width, copia.height)
  ctx.drawImage(canvas, 0, 0)
  return copia.toDataURL('image/png')
}

export function baixarPng(dataUrl: string, nomeArquivo: string): void {
  const link = document.createElement('a')
  link.href = dataUrl
  link.download = `${nomeArquivo}.png`
  link.click()
}
