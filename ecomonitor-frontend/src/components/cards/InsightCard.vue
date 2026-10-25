<script setup lang="ts">
import AppIcon from '@/components/icons/AppIcon.vue'

defineProps<{ titulo: string; texto: string; acao?: string }>()
defineEmits<{ acao: [] }>()
</script>

<template>
  <article class="insight">
    <div class="insight__texto">
      <h3 class="insight__titulo">{{ titulo }}</h3>
      <p>{{ texto }}</p>
    </div>
    <button v-if="acao" type="button" class="insight__acao" @click="$emit('acao')">
      {{ acao }}
      <AppIcon name="arrow-right" :size="14" />
    </button>
  </article>
</template>

<style scoped>
.insight {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 24px;
  padding: 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.insight__texto {
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-size: 16px;
  line-height: 25.6px;
}

.insight__titulo {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 600;
  line-height: 31.2px;
}

.insight__acao {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0;
  border: 0;
  background: none;
  color: var(--color-primary);
  font-size: 14px;
  font-weight: 700;
  line-height: 20px;
}
</style>
