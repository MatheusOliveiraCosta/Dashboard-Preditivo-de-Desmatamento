<script setup lang="ts" generic="T extends string">
export interface OpcaoToggle<V extends string> {
  valor: V
  rotulo: string
  desabilitado?: boolean
  dica?: string
}

defineProps<{ modelValue: T; opcoes: OpcaoToggle<T>[]; rotulo: string }>()
defineEmits<{ 'update:modelValue': [valor: T] }>()
</script>

<template>
  <div class="toggle" role="group" :aria-label="rotulo">
    <button
      v-for="opcao in opcoes"
      :key="opcao.valor"
      type="button"
      class="toggle__opcao"
      :class="{ 'is-ativo': opcao.valor === modelValue }"
      :aria-pressed="opcao.valor === modelValue"
      :disabled="opcao.desabilitado"
      :title="opcao.desabilitado ? opcao.dica : undefined"
      @click="$emit('update:modelValue', opcao.valor)"
    >
      {{ opcao.rotulo }}
    </button>
  </div>
</template>

<style scoped>
.toggle {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  background: #ecefea;
  border-radius: var(--radius-sm);
}

.toggle__opcao {
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: #ffffff;
  color: var(--color-text);
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
}

.toggle__opcao.is-ativo {
  background: rgba(21, 66, 18, 0.12);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.toggle__opcao:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
