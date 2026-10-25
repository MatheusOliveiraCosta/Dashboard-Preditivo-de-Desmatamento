<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ src: string; legenda: string; alt?: string }>()

// Se a foto não for encontrada, o card continua legível sobre o fundo verde escuro.
const falhou = ref(false)
</script>

<template>
  <figure class="imagem">
    <img
      v-if="!falhou"
      :src="src"
      :alt="alt ?? legenda"
      class="imagem__foto"
      @error="falhou = true"
    />
    <div class="imagem__degrade" aria-hidden="true" />
    <figcaption class="imagem__legenda">{{ legenda }}</figcaption>
  </figure>
</template>

<style scoped>
.imagem {
  position: relative;
  overflow: hidden;
  min-height: 256px;
  margin: 0;
  border-radius: var(--radius-lg);
  background: #26331f;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.imagem__foto {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.imagem__degrade {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.4) 50%, transparent);
}

.imagem__legenda {
  position: absolute;
  left: 24px;
  right: 24px;
  bottom: 24px;
  color: #ffffff;
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 600;
  line-height: 31.2px;
}
</style>
