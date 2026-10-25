<script setup lang="ts">
import { computed, ref } from 'vue'
import AppIcon from '@/components/icons/AppIcon.vue'
import type { SecaoExplicativa } from '@/content/dinamicaClimatica'

const props = defineProps<{ titulo: string; secoes: SecaoExplicativa[] }>()

// Começa mostrando só a primeira seção; "Saiba mais..." revela as demais.
const expandido = ref(false)
const visiveis = computed(() => (expandido.value ? props.secoes : props.secoes.slice(0, 1)))
const temMais = computed(() => props.secoes.length > 1)
</script>

<template>
  <aside class="painel" :aria-label="titulo">
    <h2 class="painel__titulo">
      <AppIcon name="wind" :size="24" />
      <span>{{ titulo }}</span>
    </h2>

    <section v-for="(secao, i) in visiveis" :key="secao.titulo" class="painel__secao">
      <hr v-if="i > 0" class="painel__divisor" />
      <h3 class="painel__subtitulo">{{ secao.titulo }}</h3>
      <p v-for="paragrafo in secao.paragrafos" :key="paragrafo" class="painel__texto">
        {{ paragrafo }}
      </p>
    </section>

    <template v-if="temMais">
      <hr class="painel__divisor" />
      <button
        type="button"
        class="painel__mais"
        :aria-expanded="expandido"
        @click="expandido = !expandido"
      >
        {{ expandido ? 'Mostrar menos' : 'Saiba mais...' }}
      </button>
    </template>
  </aside>
</template>

<style scoped>
.painel {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  color: #d6e7ba;
  background:
    linear-gradient(114deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0) 100%), #2f3822;
  border: 1px solid rgba(74, 79, 72, 0.3);
  border-radius: var(--radius-lg);
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -2px rgba(0, 0, 0, 0.1);
}

.painel__titulo {
  display: flex;
  align-items: center;
  gap: 16px;
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 600;
  line-height: 31.2px;
}

.painel__secao {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.painel__subtitulo {
  font-size: 14px;
  font-weight: 700;
  line-height: 19.6px;
  letter-spacing: 0.7px;
  text-transform: uppercase;
}

.painel__texto {
  font-size: 16px;
  font-weight: 500;
  line-height: 26px;
}

.painel__divisor {
  width: 100%;
  height: 1px;
  margin: 0 0 16px;
  border: 0;
  background: rgba(255, 255, 255, 0.3);
}

.painel__mais {
  width: 100%;
  padding: 2px 12px;
  border: 0;
  border-radius: 9999px;
  background: #e1e4df;
  color: #323b25;
  font-size: 14px;
  font-weight: 700;
  line-height: 19.6px;
  letter-spacing: 0.7px;
  text-transform: uppercase;
}
</style>
