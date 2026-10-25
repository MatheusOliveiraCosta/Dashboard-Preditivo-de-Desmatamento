// Conteúdo educativo ESTÁTICO do painel "Dinâmica Climática" (RF12/RF19).
// É texto de exemplo: deve ser escrito/revisado pela equipe do "Despertar para a Ciência" (RF21).
// Quando virar conteúdo editável, pode migrar para a API (tabela insight ou conteúdo estático).

export interface SecaoExplicativa {
  titulo: string
  paragrafos: string[]
}

export const DINAMICA_CLIMATICA: SecaoExplicativa[] = [
  {
    titulo: 'O ciclo de degradação',
    paragrafos: [
      'A redução contínua da precipitação impulsiona secas prolongadas. Simultaneamente, picos de temperatura aumentam a evapotranspiração da biomassa florestal remanescente.',
    ],
  },
  {
    titulo: 'Vulnerabilidade induzida',
    paragrafos: [
      'A floresta estressada termicamente e com déficit hídrico torna-se mais suscetível a incêndios rasteiros, que frequentemente são usados para consolidar a conversão da terra após a degradação seletiva.',
    ],
  },
  {
    titulo: 'Como interpretar a correlação',
    paragrafos: [
      'Correlação não é causalidade: dois indicadores podem variar juntos sem que um cause o outro. Os coeficientes mostram apenas o quanto as séries variaram em conjunto no período escolhido.',
    ],
  },
]
