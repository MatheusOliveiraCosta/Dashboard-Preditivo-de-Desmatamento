<script setup lang="ts">
import AppIcon, { type IconName } from '@/components/icons/AppIcon.vue'

defineProps<{
  titulo: string
  icone: IconName
  valor: string
  descricao: string
  // cor do número em destaque e do brilho decorativo (qualquer cor CSS)
  corValor: string
  corBrilho: string
}>()
</script>

<template>
  <article class="indicador">
    <span class="indicador__brilho" :style="{ background: corBrilho }" aria-hidden="true" />
    <header class="indicador__cabecalho">
      <AppIcon :name="icone" :size="20" />
      <h3 class="indicador__titulo">{{ titulo }}</h3>
    </header>
    <p class="indicador__valor" :style="{ color: corValor }">{{ valor }}</p>
    <p class="indicador__descricao">{{ descricao }}</p>
  </article>
</template>

<style scoped>
.indicador {
  position: relative;
  overflow: hidden;
  flex: 1 1 200px;
  min-width: 0;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #e1e4df;
  border: 1px solid rgba(144, 150, 140, 0.4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.indicador__brilho {
  position: absolute;
  top: -16px;
  right: -16px;
  width: 96px;
  height: 96px;
  border-radius: 9999px;
  filter: blur(12px);
  pointer-events: none;
}

.indicador__cabecalho {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
}

.indicador__titulo {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 600;
  line-height: 31.2px;
  color: #111312;
}

.indicador__valor {
  position: relative;
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 700;
  line-height: 36px;
  letter-spacing: -1.08px;
}

.indicador__descricao {
  position: relative;
  font-size: 14px;
  font-weight: 500;
  line-height: 19.6px;
  letter-spacing: 0.7px;
  color: #2b3028;
}
</style>
