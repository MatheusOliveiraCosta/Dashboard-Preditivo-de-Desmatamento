<script setup lang="ts">
import AppIcon, { type IconName } from '@/components/icons/AppIcon.vue'

withDefaults(
  defineProps<{
    titulo: string
    icone: IconName
    // cor do brilho decorativo no canto superior direito do card
    brilho?: 'verde' | 'marrom' | 'verde-forte'
  }>(),
  { brilho: 'verde' },
)
</script>

<template>
  <article class="kpi">
    <span class="kpi__brilho" :class="`kpi__brilho--${brilho}`" aria-hidden="true" />
    <header class="kpi__cabecalho">
      <AppIcon :name="icone" :size="20" />
      <h3 class="kpi__titulo">{{ titulo }}</h3>
    </header>
    <div class="kpi__valor">
      <slot />
    </div>
  </article>
</template>

<style scoped>
.kpi {
  position: relative;
  overflow: hidden;
  flex: 1 1 240px;
  min-width: 0;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.kpi__brilho {
  position: absolute;
  top: -40px;
  right: -40px;
  width: 128px;
  height: 128px;
  border-radius: 50%;
  filter: blur(20px);
  pointer-events: none;
}

.kpi__brilho--verde {
  background: rgba(21, 66, 18, 0.1);
}

.kpi__brilho--marrom {
  background: rgba(128, 85, 51, 0.1);
}

.kpi__brilho--verde-forte {
  background: rgba(21, 66, 18, 0.15);
}

.kpi__cabecalho {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text);
}

.kpi__titulo {
  font-size: 14px;
  font-weight: 700;
  line-height: 1.4;
  letter-spacing: 1.4px;
  text-transform: uppercase;
}

.kpi__valor {
  position: relative;
  display: flex;
  align-items: baseline;
  gap: 8px;
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 700;
  line-height: 36px;
  letter-spacing: -1.08px;
}
</style>
