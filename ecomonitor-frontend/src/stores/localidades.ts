import { ref } from 'vue'
import { defineStore } from 'pinia'
import { getLocalidades } from '@/api/localidades'
import type { Localidade } from '@/types/api'

// Lista de estados e biomas carregada uma única vez e compartilhada
// (filtros da Visão Geral, cabeçalho etc.).
export const useLocalidadesStore = defineStore('localidades', () => {
  const todas = ref<Localidade[]>([])
  const erro = ref<string | null>(null)
  let promessa: Promise<void> | null = null

  function carregar(): Promise<void> {
    if (!promessa) {
      promessa = getLocalidades()
        .then((lista) => {
          todas.value = lista
        })
        .catch((e) => {
          erro.value = e instanceof Error ? e.message : 'Não foi possível carregar as localidades.'
          promessa = null // permite tentar de novo
        })
    }
    return promessa
  }

  return { todas, erro, carregar }
})
