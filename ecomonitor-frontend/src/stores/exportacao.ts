import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export type LinhaCsv = (string | number)[]

// A tela ativa registra aqui os dados que está exibindo; o botão
// "Exportar Dados CSV" do cabeçalho baixa exatamente isso (RF16).
export const useExportacaoStore = defineStore('exportacao', () => {
  const nomeArquivo = ref('dados')
  const linhas = ref<LinhaCsv[]>([])

  const disponivel = computed(() => linhas.value.length > 1)

  function registrar(nome: string, dados: LinhaCsv[]) {
    nomeArquivo.value = nome
    linhas.value = dados
  }

  function limpar() {
    linhas.value = []
  }

  return { nomeArquivo, linhas, disponivel, registrar, limpar }
})
