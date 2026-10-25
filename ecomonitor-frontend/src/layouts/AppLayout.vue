<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'

const route = useRoute()
// Telas com meta.larguraTotal (ex.: Modo Apresentação) cuidam do próprio espaçamento e fundo.
const larguraTotal = computed(() => route.meta.larguraTotal === true)
</script>

<template>
  <div class="layout">
    <AppSidebar />
    <AppHeader />
    <main class="layout__conteudo" :class="{ 'layout__conteudo--total': larguraTotal }">
      <div class="layout__container">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout__conteudo {
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  /* 64px do cabeçalho fixo + 48px de respiro, como no Figma */
  padding: calc(var(--header-height) + 48px) 48px 48px;
}

.layout__container {
  max-width: var(--content-max-width);
  margin: 0 auto;
}

.layout__conteudo--total {
  padding: var(--header-height) 0 0;
}

.layout__conteudo--total .layout__container {
  max-width: none;
  margin: 0;
}
</style>
