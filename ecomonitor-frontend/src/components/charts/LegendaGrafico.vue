<script setup lang="ts">
export interface ItemLegenda {
  rotulo: string
  estilo: 'linha' | 'tracejado' | 'quadrado' | 'barra'
  cor: string
}

withDefaults(defineProps<{ itens: ItemLegenda[]; variante?: 'flutuante' | 'plana' }>(), {
  variante: 'flutuante',
})
</script>

<template>
  <ul class="legenda" :class="`legenda--${variante}`" aria-label="Legenda do gráfico">
    <li v-for="item in itens" :key="item.rotulo" class="legenda__item">
      <span
        class="legenda__marca"
        :class="`legenda__marca--${item.estilo}`"
        :style="item.estilo === 'tracejado' ? { borderColor: item.cor } : { background: item.cor }"
        aria-hidden="true"
      />
      {{ item.rotulo }}
    </li>
  </ul>
</template>

<style scoped>
.legenda {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  align-items: center;
  margin: 0;
  padding: 12px;
  list-style: none;
  background: rgba(247, 250, 245, 0.9);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(144, 150, 140, 0.4);
  border-radius: var(--radius-md);
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -2px rgba(0, 0, 0, 0.1);
}

.legenda--plana {
  padding: 0;
  background: none;
  backdrop-filter: none;
  border: 0;
  box-shadow: none;
}

.legenda__item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  line-height: 19.6px;
  letter-spacing: 0.7px;
  color: #111312;
  white-space: nowrap;
}

.legenda__marca {
  flex: none;
  display: inline-block;
}

.legenda__marca--linha {
  width: 16px;
  height: 4px;
  border-radius: 9999px;
}

.legenda__marca--tracejado {
  width: 16px;
  height: 4px;
  border: 1px dashed;
  border-radius: 9999px;
}

.legenda__marca--barra {
  width: 9px;
  height: 16px;
  border-radius: 2px;
}

.legenda__marca--quadrado {
  width: 16px;
  height: 16px;
  border-radius: 2px;
}
</style>
