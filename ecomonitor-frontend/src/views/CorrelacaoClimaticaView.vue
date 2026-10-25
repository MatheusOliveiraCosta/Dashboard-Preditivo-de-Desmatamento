<script setup lang="ts">
import { computed, onBeforeUnmount, watchEffect } from 'vue'
import AreaFocoCard from '@/components/cards/AreaFocoCard.vue'
import IndicadorCard from '@/components/cards/IndicadorCard.vue'
import PainelExplicativo from '@/components/cards/PainelExplicativo.vue'
import CorrelacaoChart from '@/components/charts/CorrelacaoChart.vue'
import LegendaGrafico, { type ItemLegenda } from '@/components/charts/LegendaGrafico.vue'
import AppIcon from '@/components/icons/AppIcon.vue'
import { useCorrelacaoClimatica } from '@/composables/useCorrelacaoClimatica'
import { DINAMICA_CLIMATICA } from '@/content/dinamicaClimatica'
import { useExportacaoStore } from '@/stores/exportacao'

const { dados, serie, anoInicial, anoFinal, erro, carregando } = useCorrelacaoClimatica()
const exportacao = useExportacaoStore()

const comSinal = (casas: number) =>
  new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
    signDisplay: 'exceptZero',
  })
const pct = comSinal(1)
const graus = comSinal(1)
const milimetros = comSinal(0)

const legenda: ItemLegenda[] = [
  { rotulo: 'Desmatamento (km²)', estilo: 'linha', cor: '#93000a' },
  { rotulo: 'Temperatura (°C)', estilo: 'tracejado', cor: '#b45309' },
  { rotulo: 'Precipitação (mm)', estilo: 'quadrado', cor: '#2d5a27' },
]

const indicadores = computed(() => dados.value?.indicadores ?? null)
const periodo = computed(() =>
  anoInicial.value === undefined ? '—' : `${anoInicial.value} - ${anoFinal.value}`,
)
const tituloDeficit = computed(() =>
  (indicadores.value?.deficit_hidrico_mm ?? 0) < 0 ? 'Déficit Hídrico' : 'Excedente Hídrico',
)
const supressaoEmAlta = computed(() => (indicadores.value?.taxa_supressao_pct ?? 0) > 0)

// O botão "Exportar Dados CSV" do cabeçalho baixa o que está na tela.
watchEffect(() => {
  exportacao.registrar('correlacao-climatica', [
    ['ano', 'area_desmatada_km2', 'temperatura_media_c', 'precipitacao_total_mm'],
    ...serie.value.map((p) => [p.ano, p.area_km2, p.temperatura_media_c, p.precipitacao_mm]),
  ])
})
onBeforeUnmount(() => exportacao.limpar())
</script>

<template>
  <div class="correlacao">
    <p v-if="erro" class="correlacao__erro" role="alert">{{ erro }}</p>

    <header class="correlacao__topo">
      <div class="correlacao__titulos">
        <h1 class="correlacao__titulo">Correlação Climática &amp; Vulnerabilidade Florestal</h1>
        <p class="correlacao__lide">
          {{
            dados?.insight ??
            'Compare a evolução do desmatamento com a temperatura média e a precipitação ao longo do tempo.'
          }}
        </p>
      </div>

      <div class="correlacao__acoes">
        <div class="correlacao__periodo">
          <span class="correlacao__periodo-rotulo">Período</span>
          <strong class="correlacao__periodo-valor">{{ periodo }}</strong>
        </div>
        <!-- Sem requisito definido para este botão (ver LEIA-ME): fica desabilitado por enquanto. -->
        <button
          type="button"
          class="correlacao__relatorio"
          disabled
          title="Relatório ainda não definido"
        >
          <AppIcon name="download" :size="16" />
          Baixar Relatório
        </button>
      </div>
    </header>

    <div class="correlacao__grade" :aria-busy="carregando">
      <div class="correlacao__principal">
        <section class="correlacao__grafico" aria-label="Desmatamento, temperatura e precipitação">
          <div class="correlacao__legenda">
            <LegendaGrafico :itens="legenda" />
          </div>
          <div class="correlacao__canvas">
            <CorrelacaoChart :serie="serie" />
          </div>
        </section>

        <section class="correlacao__indicadores" aria-label="Indicadores do período">
          <IndicadorCard
            titulo="Supressão"
            icone="tree"
            :valor="indicadores ? `${pct.format(indicadores.taxa_supressao_pct)}%` : '—'"
            descricao="Variação média anual do desmatamento no período."
            :cor-valor="supressaoEmAlta ? '#93000a' : '#1e3b1a'"
            :cor-brilho="supressaoEmAlta ? 'rgba(147, 0, 10, 0.2)' : 'rgba(30, 59, 26, 0.1)'"
          />
          <IndicadorCard
            titulo="Anomalia Térmica"
            icone="thermometer"
            :valor="indicadores ? `${graus.format(indicadores.anomalia_termica_c)}°C` : '—'"
            :descricao="`Desvio da temperatura média de ${anoFinal ?? '—'} em relação à média do período.`"
            cor-valor="#b45309"
            cor-brilho="rgba(180, 83, 9, 0.1)"
          />
          <IndicadorCard
            :titulo="tituloDeficit"
            icone="cloud-rain"
            :valor="indicadores ? `${milimetros.format(indicadores.deficit_hidrico_mm)}mm` : '—'"
            :descricao="`Diferença da precipitação de ${anoFinal ?? '—'} em relação à média do período.`"
            cor-valor="#1e3b1a"
            cor-brilho="rgba(30, 59, 26, 0.1)"
          />
        </section>
      </div>

      <div class="correlacao__lateral">
        <PainelExplicativo titulo="Dinâmica Climática" :secoes="DINAMICA_CLIMATICA" />
        <AreaFocoCard
          titulo="Área Foco: Arco do Desmatamento"
          src="/img/sentinel-arco-desmatamento.png"
          legenda="Satélite Sentinel-2 (Composto)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.correlacao {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.correlacao__topo {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
}

.correlacao__titulos {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1 1 480px;
  max-width: 768px;
}

.correlacao__titulo {
  font-family: var(--font-display);
  font-size: 40px;
  font-weight: 700;
  line-height: 46px;
  letter-spacing: -1.2px;
  color: #111312;
}

.correlacao__lide {
  max-width: 672px;
  font-size: 18px;
  font-weight: 500;
  line-height: 28.8px;
  color: #2b3028;
}

.correlacao__acoes {
  display: flex;
  align-items: center;
  gap: 24px;
}

.correlacao__periodo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 11px 21px;
  background: #e1e4df;
  border: 1px solid rgba(144, 150, 140, 0.5);
  border-radius: var(--radius-sm);
  filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.05));
  white-space: nowrap;
}

.correlacao__periodo-rotulo {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #2b3028;
}

.correlacao__periodo-valor {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: #0f300c;
}

.correlacao__relatorio {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--color-action);
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
  white-space: nowrap;
}

.correlacao__relatorio:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.correlacao__grade {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 24px;
  align-items: start;
}

.correlacao__principal {
  grid-column: span 9;
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-width: 0;
}

.correlacao__lateral {
  grid-column: span 3;
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-width: 0;
}

.correlacao__grafico {
  position: relative;
  padding: 57px 24px 24px;
  background: var(--color-card);
  border: 1px solid rgba(144, 150, 140, 0.3);
  border-radius: var(--radius-lg);
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -4px rgba(0, 0, 0, 0.1);
}

.correlacao__legenda {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 1;
  max-width: calc(100% - 48px);
}

.correlacao__canvas {
  position: relative;
  height: 460px;
}

.correlacao__indicadores {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.correlacao__erro {
  padding: 12px 16px;
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-sm);
  color: var(--color-danger);
}

@media (max-width: 1180px) {
  .correlacao__principal,
  .correlacao__lateral {
    grid-column: 1 / -1;
  }
}
</style>
