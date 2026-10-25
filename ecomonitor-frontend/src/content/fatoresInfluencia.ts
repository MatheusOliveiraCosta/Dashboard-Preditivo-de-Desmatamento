// Conteúdo educativo ESTÁTICO da seção "Fatores de Influência" (RF12).
// É texto de exemplo: deve ser escrito/revisado pela equipe do "Despertar para a Ciência" (RF21).
// Importante: o modelo atual usa só o histórico de desmatamento e as variáveis climáticas;
// estes fatores servem de CONTEXTO para interpretar a projeção, não entram no cálculo.

import type { IconName } from '@/components/icons/AppIcon.vue'

export interface FatorInfluencia {
  titulo: string
  descricao: string
  icone: IconName
  imagem?: string // foto de fundo opcional (public/img/fatores)
}

export const INTRODUCAO_FATORES =
  'O desmatamento é influenciado por vários fatores. A projeção desta tela usa apenas o histórico de desmatamento; os fatores abaixo ajudam a interpretar o resultado, mas não entram diretamente no cálculo.'

export const FATORES_INFLUENCIA: FatorInfluencia[] = [
  {
    titulo: 'Cobertura Florestal',
    descricao:
      'A quantidade de vegetação nativa que ainda existe na região influencia o ritmo e o impacto de novas perdas.',
    icone: 'tree',
    imagem: '/img/fatores/fator-1.jpg',
  },
  {
    titulo: 'Anomalias Climáticas',
    descricao:
      'Secas e temperaturas acima da média deixam a floresta mais vulnerável, principalmente ao fogo.',
    icone: 'wind',
    imagem: '/img/fatores/fator-2.jpg',
  },
  {
    titulo: 'Pressão Antrópica',
    descricao:
      'A expansão da agropecuária e de áreas ocupadas é uma das principais causas diretas do desmatamento.',
    icone: 'shield',
    imagem: '/img/fatores/fator-3.jpg',
  },
]
