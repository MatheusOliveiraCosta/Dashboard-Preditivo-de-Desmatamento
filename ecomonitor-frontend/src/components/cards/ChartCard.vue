<script setup lang="ts">
import AppIcon from '@/components/icons/AppIcon.vue'

defineProps<{ titulo: string; subtitulo?: string }>()
defineEmits<{ ampliar: [] }>()
</script>

<template>
  <section class="chart-card">
    <header class="chart-card__cabecalho">
      <div>
        <h2 class="chart-card__titulo">{{ titulo }}</h2>
        <p v-if="subtitulo" class="chart-card__subtitulo">{{ subtitulo }}</p>
      </div>
      <button
        type="button"
        class="chart-card__ampliar"
        aria-label="Ampliar gráfico"
        @click="$emit('ampliar')"
      >
        <AppIcon name="expand" :size="16" />
      </button>
    </header>
    <div class="chart-card__corpo">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.chart-card {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.chart-card__cabecalho {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.chart-card__titulo {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 600;
  line-height: 38.4px;
  letter-spacing: -0.32px;
}

.chart-card__subtitulo {
  color: var(--color-text-muted);
  font-size: 16px;
  line-height: 25.6px;
}

.chart-card__ampliar {
  display: grid;
  place-items: center;
  flex: none;
  width: 34px;
  height: 34px;
  border: 1px solid var(--color-border);
  border-radius: 9999px;
  background: var(--color-surface);
  color: var(--color-text);
}

.chart-card__corpo {
  position: relative;
  height: 340px;
}
</style>
