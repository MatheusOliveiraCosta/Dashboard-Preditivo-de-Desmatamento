<script setup lang="ts">
import { computed, onBeforeUnmount, watchEffect } from 'vue'
import ChartCard from '@/components/cards/ChartCard.vue'
import ImageCard from '@/components/cards/ImageCard.vue'
import InsightCard from '@/components/cards/InsightCard.vue'
import KpiCard from '@/components/cards/KpiCard.vue'
import HistoricoChart from '@/components/charts/HistoricoChart.vue'
import FilterBar from '@/components/filters/FilterBar.vue'
import AppIcon from '@/components/icons/AppIcon.vue'
import { useOverview } from '@/composables/useOverview'
import { useExportacaoStore } from '@/stores/exportacao'

const { dados, kpi, serie, carregando, erro } = useOverview()
const exportacao = useExportacaoStore()

const numero = new Intl.NumberFormat('pt-BR')
const percentual = new Intl.NumberFormat('pt-BR', {
  maximumFractionDigits: 0,
  signDisplay: 'exceptZero',
})

const anoInicial = computed(() => serie.value[0]?.ano)
const anoFinal = computed(() => serie.value[serie.value.length - 1]?.ano)

const subtitulo = computed(() =>
  anoInicial.value === undefined
    ? ''
    : anoInicial.value === anoFinal.value
      ? `Área desmatada (km²) em ${anoFinal.value}.`
      : `Evolução anual da área desmatada (km²) no período de ${anoInicial.value} a ${anoFinal.value}.`,
)

// Queda no desmatamento é a "boa notícia" (verde); alta fica em vermelho.
const tendenciaCrescente = computed(() => (kpi.value?.variacao_percentual ?? 0) > 0)

// O botão "Exportar Dados CSV" do cabeçalho baixa o que está na tela.
watchEffect(() => {
  exportacao.registrar('desmatamento-historico', [
    ['ano', 'area_desmatada_km2'],
    ...serie.value.map((ponto) => [ponto.ano, ponto.area_km2]),
  ])
})
onBeforeUnmount(() => exportacao.limpar())
</script>

<template>
  <div class="visao-geral">
    <p v-if="erro" class="visao-geral__erro" role="alert">{{ erro }}</p>

    <section class="visao-geral__kpis" aria-label="Indicadores" :aria-busy="carregando">
      <KpiCard :titulo="`Taxa (${kpi?.ano_referencia ?? '—'})`" icone="tree" brilho="verde">
        <span>{{ kpi ? numero.format(kpi.area_desmatada_km2) : '—' }}</span>
        <span class="visao-geral__unidade">km²</span>
      </KpiCard>

      <KpiCard titulo="Bioma crítico" icone="mountain" brilho="marrom">
        <span>{{ dados?.bioma_critico ?? '—' }}</span>
      </KpiCard>

      <KpiCard titulo="Tendência interanual" icone="trending-down" brilho="verde-forte">
        <span
          class="visao-geral__tendencia"
          :class="{ 'visao-geral__tendencia--alta': tendenciaCrescente }"
        >
          <AppIcon :name="tendenciaCrescente ? 'trending-up' : 'trending-down'" :size="28" />
          {{ kpi ? `${percentual.format(kpi.variacao_percentual)}%` : '—' }}
        </span>
      </KpiCard>
    </section>

    <FilterBar :ano-inicial="anoInicial" :ano-final="anoFinal" />

    <ChartCard titulo="Histórico de Desmatamento" :subtitulo="subtitulo">
      <HistoricoChart :serie="serie" />
    </ChartCard>

    <section class="visao-geral__detalhes">
      <ImageCard src="/img/fronteira-expansao-para.jpg" legenda="Fronteira de Expansão - Pará" />
      <InsightCard
        titulo="Análise de Redução"
        :texto="dados?.insight ?? ''"
        acao="Ler Relatório Completo"
      />
    </section>
  </div>
</template>

<style scoped>
.visao-geral {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.visao-geral__kpis {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 56px; /* 24 + 56 = 80px entre os cards e os filtros, como no Figma */
}

.visao-geral__unidade {
  font-size: 24px;
  font-weight: 600;
  line-height: 31.2px;
  letter-spacing: 0;
}

.visao-geral__tendencia {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--color-primary);
}

.visao-geral__tendencia--alta {
  color: var(--color-danger);
}

.visao-geral__detalhes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  margin-top: 56px;
}

.visao-geral__erro {
  padding: 12px 16px;
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-sm);
  color: var(--color-danger);
}
</style>
