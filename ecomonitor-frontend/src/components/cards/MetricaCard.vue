<script setup lang="ts">
import AppIcon from '@/components/icons/AppIcon.vue'

withDefaults(
  defineProps<{
    rotulo: string
    valor: string
    unidade: string
    tom?: 'claro' | 'escuro'
    tendencia?: 'queda' | 'alta' | null
  }>(),
  { tom: 'claro', tendencia: null },
)
</script>

<template>
  <article class="metrica" :class="`metrica--${tom}`">
    <p class="metrica__rotulo">{{ rotulo }}</p>
    <div class="metrica__valor">
      <span class="metrica__numero">{{ valor }}</span>
      <span class="metrica__unidade">{{ unidade }}</span>
      <AppIcon
        v-if="tendencia"
        class="metrica__tendencia"
        :name="tendencia === 'queda' ? 'trending-down' : 'trending-up'"
        :size="20"
      />
    </div>
  </article>
</template>

<style scoped>
.metrica {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px;
  border: 1px solid;
  border-radius: var(--radius-lg);
}

.metrica--claro {
  background: #ffffff;
  border-color: rgba(194, 201, 187, 0.6);
  box-shadow: 0 4px 6px rgba(10, 38, 8, 0.06);
  --cor-rotulo: #42493e;
  --cor-numero: #111412;
  --cor-unidade: #42493e;
}

.metrica--escuro {
  background: #0a2608;
  border-color: #0a2608;
  box-shadow: 0 4px 6px rgba(10, 38, 8, 0.18);
  --cor-rotulo: #b8f0ab;
  --cor-numero: #ffffff;
  --cor-unidade: #d6e8d0;
}

.metrica__rotulo {
  font-size: 12px;
  font-weight: 700;
  line-height: 16px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--cor-rotulo);
}

.metrica__valor {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.metrica__numero {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  line-height: 40px;
  color: var(--cor-numero);
}

.metrica__unidade {
  font-size: 16px;
  font-weight: 700;
  line-height: 24px;
  color: var(--cor-unidade);
}

.metrica__tendencia {
  align-self: center;
  margin-left: auto;
  color: var(--cor-rotulo);
}
</style>
