<script setup lang="ts">
import { computed, onBeforeUnmount, watchEffect } from 'vue'
import FatorCard from '@/components/cards/FatorCard.vue'
import MetricaCard from '@/components/cards/MetricaCard.vue'
import LegendaGrafico, { type ItemLegenda } from '@/components/charts/LegendaGrafico.vue'
import ProjecaoChart from '@/components/charts/ProjecaoChart.vue'
import ToggleSegmentado, { type OpcaoToggle } from '@/components/filters/ToggleSegmentado.vue'
import AppIcon from '@/components/icons/AppIcon.vue'
import { useProjecaoTendencia, type TipoVisao } from '@/composables/useProjecaoTendencia'
import { FATORES_INFLUENCIA, INTRODUCAO_FATORES } from '@/content/fatoresInfluencia'
import { useExportacaoStore } from '@/stores/exportacao'

const {
  visao,
  tipoVisao,
  regionalDisponivel,
  base,
  final,
  primeiroAnoProjetado,
  erro,
  carregando,
} = useProjecaoTendencia()
const exportacao = useExportacaoStore()

const numero = new Intl.NumberFormat('pt-BR')

const opcoes = computed<OpcaoToggle<TipoVisao>[]>(() => [
  { valor: 'geral', rotulo: 'Geral' },
  {
    valor: 'regional',
    rotulo: 'Regional',
    desabilitado: !regionalDisponivel.value,
    dica: 'Selecione um estado ou bioma na Visão Geral para ver a projeção regional.',
  },
])

const legenda = computed<ItemLegenda[]>(() => [
  { rotulo: `Histórico (Até ${base.value?.ano ?? '—'})`, estilo: 'barra', cor: '#0a2608' },
  {
    rotulo: `Projeção (${primeiroAnoProjetado.value ?? '—'}-${final.value?.ano ?? '—'})`,
    estilo: 'tracejado',
    cor: '#1a2410',
  },
  { rotulo: 'Margem de Incerteza (95%)', estilo: 'barra', cor: 'rgba(214, 122, 58, 0.6)' },
])

const tendencia = computed(() => {
  if (!base.value || !final.value) return null
  return final.value.valor_projetado_km2 < base.value.area_km2 ? 'queda' : 'alta'
})

// O botão "Exportar Dados CSV" do cabeçalho baixa o que está na tela.
watchEffect(() => {
  const v = visao.value
  if (!v) return
  exportacao.registrar(`projecao-${tipoVisao.value}`, [
    ['ano', 'tipo', 'area_km2', 'limite_inferior_km2', 'limite_superior_km2'],
    ...v.serie_historica.map((p) => [p.ano, 'historico', p.area_km2, '', '']),
    ...v.projecao.map((p) => [
      p.ano,
      'projecao',
      p.valor_projetado_km2,
      p.intervalo_inferior,
      p.intervalo_superior,
    ]),
  ])
})
onBeforeUnmount(() => exportacao.limpar())
</script>

<template>
  <div class="projecao">
    <p v-if="erro" class="projecao__erro" role="alert">{{ erro }}</p>

    <h1 class="projecao__titulo">Projeção <span>de Tendência</span></h1>

    <div class="projecao__grade" :aria-busy="carregando">
      <div class="projecao__resumo">
        <p class="projecao__lide">{{ visao?.insight ?? '' }}</p>
        <div class="projecao__metricas">
          <MetricaCard
            :rotulo="`Ano base (${base?.ano ?? '—'})`"
            :valor="base ? numero.format(base.area_km2) : '—'"
            unidade="km²"
          />
          <MetricaCard
            :rotulo="`Projeção (${final?.ano ?? '—'})`"
            :valor="final ? numero.format(final.valor_projetado_km2) : '—'"
            unidade="km²"
            tom="escuro"
            :tendencia="tendencia"
          />
        </div>
      </div>

      <section class="projecao__grafico" aria-label="Histórico e projeção do desmatamento">
        <header class="projecao__cabecalho">
          <LegendaGrafico :itens="legenda" variante="plana" />
          <ToggleSegmentado v-model="tipoVisao" :opcoes="opcoes" rotulo="Tipo de projeção" />
        </header>
        <div class="projecao__canvas">
          <ProjecaoChart v-if="visao" :visao="visao" />
        </div>
      </section>
    </div>

    <div class="projecao__contexto">
      <div class="projecao__fatores-texto">
        <h2 class="projecao__fatores-titulo">Fatores de Influência</h2>
        <p>{{ INTRODUCAO_FATORES }}</p>
        <!-- Sem destino definido (RF19 / UC12): por enquanto o botão não faz nada. -->
        <button type="button" class="projecao__metodologia">
          Explorar Metodologia
          <AppIcon name="arrow-right" :size="16" />
        </button>
      </div>
      <div class="projecao__fatores">
        <FatorCard
          v-for="fator in FATORES_INFLUENCIA"
          :key="fator.titulo"
          :titulo="fator.titulo"
          :descricao="fator.descricao"
          :icone="fator.icone"
          :imagem="fator.imagem"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.projecao {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.projecao__titulo {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 700;
  line-height: 52.8px;
  letter-spacing: -0.96px;
  color: #111412;
}

.projecao__titulo span {
  color: #0a2608;
}

.projecao__grade,
.projecao__contexto {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 24px;
  align-items: start;
}

.projecao__resumo {
  grid-column: span 3;
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-width: 0;
}

.projecao__lide {
  padding-right: 24px;
  font-size: 16px;
  font-weight: 500;
  line-height: 26px;
  color: #2b3328;
}

.projecao__metricas {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.projecao__grafico {
  grid-column: span 9;
  display: flex;
  flex-direction: column;
  gap: 32px;
  min-width: 0;
  padding: 48px;
  background: #ffffff;
  border-radius: 24px;
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -4px rgba(0, 0, 0, 0.1);
}

.projecao__cabecalho {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.projecao__canvas {
  position: relative;
  height: 400px;
}

.projecao__fatores-texto {
  grid-column: span 4;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
  font-size: 16px;
  font-weight: 500;
  line-height: 25.6px;
  color: #2b3328;
}

.projecao__fatores-titulo {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  line-height: 31.2px;
  color: #111412;
}

.projecao__metodologia {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  border: 0;
  background: none;
  color: var(--color-primary);
  font-size: 14px;
  font-weight: 700;
  line-height: 20px;
}

.projecao__fatores {
  grid-column: span 8;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  min-width: 0;
}

.projecao__erro {
  padding: 12px 16px;
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-sm);
  color: var(--color-danger);
}

@media (max-width: 1180px) {
  .projecao__resumo,
  .projecao__grafico,
  .projecao__fatores-texto,
  .projecao__fatores {
    grid-column: 1 / -1;
  }

  .projecao__grafico {
    padding: 24px;
  }
}
</style>
