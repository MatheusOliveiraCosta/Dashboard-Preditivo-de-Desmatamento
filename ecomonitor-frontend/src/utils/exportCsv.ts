import type { LinhaCsv } from '@/stores/exportacao'

function formatar(valor: string | number): string {
  // Excel em português usa vírgula decimal e ponto e vírgula como separador.
  const texto = typeof valor === 'number' ? String(valor).replace('.', ',') : valor
  return /[;"\r\n]/.test(texto) ? `"${texto.replace(/"/g, '""')}"` : texto
}

export function baixarCsv(nomeArquivo: string, linhas: LinhaCsv[]): void {
  const conteudo = linhas.map((linha) => linha.map(formatar).join(';')).join('\r\n')
  // O BOM no início faz o Excel reconhecer os acentos (UTF-8).
  const blob = new Blob(['\uFEFF' + conteudo], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${nomeArquivo}.csv`
  link.click()
  URL.revokeObjectURL(url)
}
