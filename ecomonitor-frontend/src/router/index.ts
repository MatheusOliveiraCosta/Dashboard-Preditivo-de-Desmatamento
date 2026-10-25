import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import type { IconName } from '@/components/icons/AppIcon.vue'

declare module 'vue-router' {
  interface RouteMeta {
    titulo?: string
    icone?: IconName
    larguraTotal?: boolean
  }
}

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'visao-geral',
          meta: { titulo: 'Visão Geral', icone: 'map' },
          component: () => import('@/views/VisaoGeralView.vue'),
        },
        {
          path: 'correlacao-climatica',
          name: 'correlacao-climatica',
          meta: { titulo: 'Correlação Climática', icone: 'thermometer' },
          component: () => import('@/views/CorrelacaoClimaticaView.vue'),
        },
        {
          path: 'projecao-tendencia',
          name: 'projecao-tendencia',
          meta: { titulo: 'Projeção de Tendência', icone: 'trending-up' },
          component: () => import('@/views/ProjecaoTendenciaView.vue'),
        },
        {
          path: 'modo-apresentacao',
          name: 'modo-apresentacao',
          meta: { titulo: 'Modo Apresentação', icone: 'present', larguraTotal: true },
          component: () => import('@/views/ModoApresentacaoView.vue'),
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})
