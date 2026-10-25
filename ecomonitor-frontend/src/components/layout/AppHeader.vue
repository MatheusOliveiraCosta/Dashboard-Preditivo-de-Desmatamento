<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from '@/components/icons/AppIcon.vue'
import { useLocalidades } from '@/composables/useLocalidades'
import { useExportacaoStore } from '@/stores/exportacao'
import { useFiltrosStore } from '@/stores/filtros'
import { baixarCsv } from '@/utils/exportCsv'

const exportacao = useExportacaoStore()
const filtros = useFiltrosStore()
const { todas } = useLocalidades()

// Mostra em todas as telas qual estado ou bioma está ativo (ou Brasil).
const localidadeAtiva = computed(
  () => todas.value.find((l) => l.id === filtros.localidadeId)?.nome ?? 'Brasil',
)

function exportar() {
  if (exportacao.disponivel) baixarCsv(exportacao.nomeArquivo, exportacao.linhas)
}
</script>

<template>
  <header class="header">
    <p class="header__contexto">
      <span>Monitoramento de Deflorestação</span>
      <AppIcon name="chevron-right" :size="12" />
      <span>{{ localidadeAtiva }}</span>
    </p>

    <div class="header__acoes">
      <span class="header__divisor" aria-hidden="true" />
      <button
        type="button"
        class="header__exportar"
        :disabled="!exportacao.disponivel"
        @click="exportar"
      >
        <AppIcon name="download" :size="16" />
        Exportar Dados CSV
      </button>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: var(--sidebar-width);
  right: 0;
  height: var(--header-height);
  padding: 0 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(247, 250, 245, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(194, 201, 187, 0.3);
  box-shadow: 0 1px 8px rgba(0, 0, 0, 0.04);
  z-index: 10;
}

.header__contexto {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  line-height: 16px;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.header__acoes {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header__divisor {
  width: 1px;
  height: 16px;
  background: #52594e;
}

.header__exportar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--color-action);
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
  filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.08));
}

.header__exportar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
