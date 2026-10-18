import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        { path: '', name: 'visao-geral', meta: { titulo: 'Visão Geral' },
          component: () => import('@/views/VisaoGeralView.vue') },
        { path: 'correlacao-climatica', name: 'correlacao-climatica', meta: { titulo: 'Correlação Climática' },
          component: () => import('@/views/CorrelacaoClimaticaView.vue') },
        { path: 'projecao-tendencia', name: 'projecao-tendencia', meta: { titulo: 'Projeção de Tendência' },
          component: () => import('@/views/ProjecaoTendenciaView.vue') },
        { path: 'modo-apresentacao', name: 'modo-apresentacao', meta: { titulo: 'Modo Apresentação' },
          component: () => import('@/views/ModoApresentacaoView.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})