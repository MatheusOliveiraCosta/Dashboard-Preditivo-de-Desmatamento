<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from '@/components/icons/AppIcon.vue'
import HexagonoFiltro from '@/components/icons/HexagonoFiltro.vue'
import { useLocalidades } from '@/composables/useLocalidades'
import { useFiltrosStore } from '@/stores/filtros'

const props = defineProps<{ anoInicial?: number; anoFinal?: number }>()

const filtros = useFiltrosStore()
const { estados, biomas, todas } = useLocalidades()

const localidadeAtiva = computed(
  () => todas.value.find((l) => l.id === filtros.localidadeId)?.nome ?? 'Brasil',
)

const descricaoPeriodo = computed(() => {
  if (filtros.periodo === '1ano') return 'último ano'
  if (filtros.periodo === '5anos') return 'últimos 5 anos'
  return 'histórico completo'
})

const intervalo = computed(() => {
  if (props.anoInicial === undefined || props.anoFinal === undefined) return ''
  return props.anoInicial === props.anoFinal
    ? ` (${props.anoFinal})`
    : ` (${props.anoInicial}–${props.anoFinal})`
})

function aoMudar(evento: Event, tipo: 'estado' | 'bioma') {
  const valor = (evento.target as HTMLSelectElement).value
  const id = valor === '' ? null : Number(valor)
  if (tipo === 'estado') filtros.selecionarEstado(id)
  else filtros.selecionarBioma(id)
}
</script>

<template>
  <section class="filtros" aria-label="Filtros">
    <div class="filtros__linha">
      <div class="filtros__espacial">
        <HexagonoFiltro />
        <div>
          <p class="filtros__rotulo">Filtro espacial</p>
          <p class="filtros__valor">{{ localidadeAtiva }}</p>
        </div>
      </div>

      <label class="filtros__select">
        <span class="sr-only">Estado</span>
        <select :value="filtros.estadoId ?? ''" @change="aoMudar($event, 'estado')">
          <option value="">Todos os Estados</option>
          <option v-for="estado in estados" :key="estado.id" :value="estado.id">
            {{ estado.nome }}
          </option>
        </select>
        <AppIcon name="chevron-down" :size="16" />
      </label>

      <label class="filtros__select">
        <span class="sr-only">Bioma</span>
        <select :value="filtros.biomaId ?? ''" @change="aoMudar($event, 'bioma')">
          <option value="">Todos os Biomas</option>
          <option v-for="bioma in biomas" :key="bioma.id" :value="bioma.id">
            {{ bioma.nome }}
          </option>
        </select>
        <AppIcon name="chevron-down" :size="16" />
      </label>
    </div>

    <div class="filtros__linha filtros__linha--periodo">
      <button
        type="button"
        class="filtros__periodo"
        :class="{ 'is-ativo': filtros.periodo === '1ano' }"
        :aria-pressed="filtros.periodo === '1ano'"
        @click="filtros.alternarPeriodo('1ano')"
      >
        1 Ano
      </button>
      <button
        type="button"
        class="filtros__periodo"
        :class="{ 'is-ativo': filtros.periodo === '5anos' }"
        :aria-pressed="filtros.periodo === '5anos'"
        @click="filtros.alternarPeriodo('5anos')"
      >
        5 Anos
      </button>
      <p class="filtros__descricao">
        Exibindo <strong>{{ descricaoPeriodo }}</strong
        >{{ intervalo }}
      </p>
    </div>
  </section>
</template>

<style scoped>
.filtros {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.filtros__linha {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
}

.filtros__linha--periodo {
  gap: 8px;
}

.filtros__espacial {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-right: 17px;
  margin-right: 1px;
  border-right: 1px solid var(--color-border-strong);
}

.filtros__rotulo {
  font-size: 10px;
  font-weight: 700;
  line-height: 15px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--color-primary);
}

.filtros__valor {
  font-size: 12px;
  font-weight: 600;
  line-height: 16px;
}

.filtros__select {
  position: relative;
  display: block;
  width: 200px;
}

.filtros__select select {
  width: 100%;
  height: 38px;
  padding: 0 36px 0 16px;
  appearance: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-card);
  color: var(--color-text);
  font: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.filtros__select svg {
  position: absolute;
  top: 11px;
  right: 12px;
  pointer-events: none;
  color: var(--color-text-muted);
}

.filtros__periodo {
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-card);
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
}

.filtros__periodo.is-ativo {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #ffffff;
}

.filtros__descricao {
  margin-left: 8px;
  font-size: 14px;
  line-height: 20px;
  color: var(--color-text-muted);
}

.filtros__descricao strong {
  color: var(--color-primary);
}
</style>
