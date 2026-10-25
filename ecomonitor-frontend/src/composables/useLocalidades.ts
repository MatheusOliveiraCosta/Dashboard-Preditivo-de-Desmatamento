import { computed, onMounted } from 'vue'
import { useLocalidadesStore } from '@/stores/localidades'

export function useLocalidades() {
  const store = useLocalidadesStore()

  onMounted(() => {
    void store.carregar()
  })

  const todas = computed(() => store.todas)
  const erro = computed(() => store.erro)
  const estados = computed(() => store.todas.filter((l) => l.tipo === 'ESTADO'))
  const biomas = computed(() => store.todas.filter((l) => l.tipo === 'BIOMA'))

  return { todas, estados, biomas, erro }
}
