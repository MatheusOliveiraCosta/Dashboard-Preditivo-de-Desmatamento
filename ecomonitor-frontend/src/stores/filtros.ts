import { defineStore } from 'pinia'

export const useFiltrosStore = defineStore('filtros', {
  state: () => ({
    localidadeId: null as number | null,   // null = Brasil
    periodo: 'historico' as '1ano' | '5anos' | 'historico',
  }),
})