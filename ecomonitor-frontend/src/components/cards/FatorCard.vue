<script setup lang="ts">
import AppIcon, { type IconName } from '@/components/icons/AppIcon.vue'

defineProps<{ titulo: string; descricao: string; icone: IconName; imagem?: string }>()
</script>

<template>
  <article class="fator">
    <!-- foto de fundo decorativa (20% de opacidade, em tons de cinza); se não existir, não aparece -->
    <span
      v-if="imagem"
      class="fator__fundo"
      :style="{ backgroundImage: `url(${imagem})` }"
      aria-hidden="true"
    />
    <div class="fator__conteudo">
      <AppIcon :name="icone" :size="28" class="fator__icone" />
      <h3 class="fator__titulo">{{ titulo }}</h3>
      <p class="fator__descricao">{{ descricao }}</p>
    </div>
  </article>
</template>

<style scoped>
.fator {
  position: relative;
  overflow: hidden;
  flex: 1 1 180px;
  min-width: 0;
  padding: 24px;
  background: #ecefea;
  border-radius: var(--radius-lg);
}

.fator__fundo {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  mix-blend-mode: multiply;
  filter: grayscale(1);
  opacity: 0.2;
  pointer-events: none;
}

.fator__conteudo {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fator__icone {
  color: var(--color-primary);
}

.fator__titulo {
  padding-top: 8px;
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  line-height: 28px;
  color: #111412;
}

.fator__descricao {
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  color: #111412;
}
</style>
