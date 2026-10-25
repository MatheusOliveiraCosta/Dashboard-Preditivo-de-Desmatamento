<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import AppIcon from '@/components/icons/AppIcon.vue'
import LogoEcoMonitor from '@/components/icons/LogoEcoMonitor.vue'

const router = useRouter()

// O menu é montado a partir das rotas filhas do layout (meta.titulo / meta.icone),
// assim os nomes ficam definidos em um único lugar: router/index.ts.
const itens = computed(() => {
  const raiz = router.options.routes.find((rota) => rota.path === '/')
  return (raiz?.children ?? []).filter((rota) => rota.meta?.titulo)
})
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__marca">
      <LogoEcoMonitor />
      <span class="sidebar__nome">EcoMonitor</span>
    </div>

    <nav aria-label="Navegação principal">
      <ul class="sidebar__lista">
        <li v-for="item in itens" :key="String(item.name)">
          <RouterLink :to="{ name: item.name }" class="sidebar__link" exact-active-class="is-ativo">
            <AppIcon v-if="item.meta?.icone" :name="item.meta.icone" :size="20" />
            <span>{{ item.meta?.titulo }}</span>
          </RouterLink>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  width: var(--sidebar-width);
  padding: 24px 16px;
  background: var(--color-surface);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  z-index: 20;
}

.sidebar__marca {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 40px;
  padding: 0 16px;
  margin-bottom: 32px;
}

.sidebar__nome {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--color-primary);
}

.sidebar__lista {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.sidebar__link {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 48px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: 16px;
  line-height: 24px;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: background-color 0.15s;
}

.sidebar__link:hover {
  background: rgba(26, 59, 22, 0.05);
}

.sidebar__link.is-ativo {
  background: var(--color-nav-active);
  color: var(--color-primary);
  font-weight: 700;
}
</style>
