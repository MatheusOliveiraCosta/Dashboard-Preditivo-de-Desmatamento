<script setup lang="ts">
import { ref } from 'vue'
import AppIcon from '@/components/icons/AppIcon.vue'

defineProps<{ titulo: string; src: string; legenda: string }>()

// Se a imagem não for encontrada, o quadro continua legível sobre o fundo escuro.
const falhou = ref(false)
</script>

<template>
  <figure class="foco">
    <figcaption class="foco__titulo">
      <AppIcon name="map-pin" :size="14" />
      <span>{{ titulo }}</span>
    </figcaption>
    <div class="foco__quadro">
      <img v-if="!falhou" :src="src" :alt="legenda" class="foco__imagem" @error="falhou = true" />
      <div class="foco__degrade" aria-hidden="true" />
      <p class="foco__legenda">{{ legenda }}</p>
    </div>
  </figure>
</template>

<style scoped>
.foco {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
  padding: 16px;
  background: var(--color-card);
  border: 1px solid rgba(144, 150, 140, 0.4);
  border-radius: var(--radius-lg);
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
}

.foco__titulo {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  line-height: 19.6px;
  letter-spacing: 0.7px;
  color: #111312;
}

.foco__titulo svg {
  flex: none;
  margin-top: 3px;
}

.foco__quadro {
  position: relative;
  overflow: hidden;
  height: 192px;
  border-radius: var(--radius-md);
  background: #26331f;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.foco__imagem {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.foco__degrade {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0));
}

.foco__legenda {
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 12px;
  color: #ffffff;
  font-size: 14px;
  font-weight: 700;
  line-height: 19.6px;
  letter-spacing: 0.7px;
}
</style>
