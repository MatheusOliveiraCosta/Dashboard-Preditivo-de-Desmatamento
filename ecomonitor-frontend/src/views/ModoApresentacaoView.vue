<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watchEffect } from 'vue'
import ApresentacaoLinhaChart from '@/components/charts/ApresentacaoLinhaChart.vue'
import ProjecaoChart from '@/components/charts/ProjecaoChart.vue'
import AppIcon from '@/components/icons/AppIcon.vue'
import { useApresentacao } from '@/composables/useApresentacao'
import { useExportacaoStore } from '@/stores/exportacao'
import { formatarCompacto } from '@/utils/formatar'
import { baixarPng } from '@/utils/exportPng'

const {
  slides,
  indice,
  slide,
  proximo,
  anterior,
  serieEvolucao,
  totalAcumulado,
  visaoProjecao,
  valorFinalProjecao,
  erro,
} = useApresentacao()
const exportacao = useExportacaoStore()

// Métrica em destaque (canto superior esquerdo do gráfico) de cada slide.
const metrica = computed(() => {
  if (slide.value.id === 'evolucao') {
    return { rotulo: 'Total acumulado', valor: formatarCompacto(totalAcumulado.value) }
  }
  const final = valorFinalProjecao.value
  return {
    rotulo: `Projeção (${final?.ano ?? '—'})`,
    valor: final ? formatarCompacto(final.valor_projetado_km2) : '—',
  }
})

// Gráfico exibido agora (usado pelo botão "Exportar Gráfico PNG").
const grafico = ref<InstanceType<typeof ApresentacaoLinhaChart | typeof ProjecaoChart> | null>(null)

function exportarGrafico() {
  const imagem = grafico.value?.exportarPng()
  if (imagem) baixarPng(imagem, `grafico-${slide.value.id}`)
}

// O botão "Exportar Dados CSV" do cabeçalho baixa os dados do gráfico exibido.
watchEffect(() => {
  if (slide.value.id === 'evolucao') {
    exportacao.registrar('evolucao-desmatamento', [
      ['ano', 'area_desmatada_km2'],
      ...serieEvolucao.value.map((p) => [p.ano, p.area_km2]),
    ])
    return
  }
  const v = visaoProjecao.value
  exportacao.registrar('projecao-desmatamento', [
    ['ano', 'tipo', 'area_km2', 'limite_inferior_km2', 'limite_superior_km2'],
    ...(v?.serie_historica ?? []).map((p) => [p.ano, 'historico', p.area_km2, '', '']),
    ...(v?.projecao ?? []).map((p) => [
      p.ano,
      'projecao',
      p.valor_projetado_km2,
      p.intervalo_inferior,
      p.intervalo_superior,
    ]),
  ])
})

// Setas do teclado passam os gráficos, útil em apresentações com controle remoto.
function aoTeclar(evento: KeyboardEvent) {
  if (evento.key === 'ArrowRight') proximo()
  else if (evento.key === 'ArrowLeft') anterior()
}
onMounted(() => window.addEventListener('keydown', aoTeclar))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', aoTeclar)
  exportacao.limpar()
})
</script>

<template>
  <div class="apresentacao">
    <span class="apresentacao__brilho apresentacao__brilho--verde" aria-hidden="true" />
    <span class="apresentacao__brilho apresentacao__brilho--laranja" aria-hidden="true" />

    <div class="apresentacao__conteudo">
      <p v-if="erro" class="apresentacao__erro" role="alert">{{ erro }}</p>

      <header class="apresentacao__topo">
        <h1 class="apresentacao__titulo">
          {{ slide.titulo[0] }}<br />
          {{ slide.titulo[1] }}
        </h1>
        <button type="button" class="apresentacao__exportar" @click="exportarGrafico">
          <AppIcon name="download" :size="16" />
          Exportar Gráfico PNG
        </button>
      </header>

      <hr class="apresentacao__separador" />

      <section
        class="apresentacao__grafico"
        :aria-label="`Gráfico ${indice + 1} de ${slides.length}`"
      >
        <div class="apresentacao__metrica">
          <div>
            <p class="apresentacao__metrica-rotulo">{{ metrica.rotulo }}</p>
            <p class="apresentacao__metrica-valor">
              {{ metrica.valor }}
              <span class="apresentacao__metrica-unidade">km²</span>
            </p>
          </div>
          <span class="apresentacao__metrica-divisor" aria-hidden="true" />
        </div>

        <div class="apresentacao__canvas">
          <ApresentacaoLinhaChart
            v-if="slide.id === 'evolucao'"
            ref="grafico"
            :serie="serieEvolucao"
          />
          <ProjecaoChart v-else-if="visaoProjecao" ref="grafico" :visao="visaoProjecao" />
        </div>
      </section>

      <footer class="apresentacao__rodape">
        <p class="apresentacao__status" aria-live="polite">
          <span class="apresentacao__ponto" aria-hidden="true" />
          Modo Apresentação ativo · Gráfico {{ indice + 1 }} de {{ slides.length }}
        </p>
        <div class="apresentacao__controles">
          <button
            type="button"
            class="apresentacao__seta"
            aria-label="Gráfico anterior"
            @click="anterior"
          >
            <AppIcon name="chevron-left" :size="20" />
          </button>
          <button
            type="button"
            class="apresentacao__seta"
            aria-label="Próximo gráfico"
            @click="proximo"
          >
            <AppIcon name="chevron-right" :size="20" />
          </button>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.apresentacao {
  position: relative;
  overflow: hidden;
  min-height: calc(100vh - var(--header-height));
  padding: 40px 48px 48px;
  background: #ffffff;
}

.apresentacao__brilho {
  position: absolute;
  border-radius: 9999px;
  pointer-events: none;
}

.apresentacao__brilho--verde {
  top: 0;
  right: 0;
  width: 384px;
  height: 384px;
  background: rgba(26, 59, 22, 0.1);
  filter: blur(50px);
}

.apresentacao__brilho--laranja {
  bottom: 0;
  left: 80px;
  width: 320px;
  height: 320px;
  background: rgba(253, 195, 154, 0.1);
  filter: blur(40px);
}

.apresentacao__conteudo {
  position: relative;
  max-width: var(--content-max-width);
  margin: 0 auto;
}

.apresentacao__topo {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 8px;
}

.apresentacao__titulo {
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 800;
  line-height: 60px;
  letter-spacing: -0.96px;
  color: var(--color-text);
}

.apresentacao__exportar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--color-action);
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  line-height: 20px;
  filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.08));
}

.apresentacao__separador {
  height: 1px;
  margin: 40px 0 24px;
  border: 0;
  background: var(--color-border);
}

.apresentacao__grafico {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 48px 32px 32px;
  background: var(--color-bg);
  border: 1px solid rgba(194, 201, 187, 0.5);
  border-radius: 32px;
  box-shadow: var(--shadow-card);
}

.apresentacao__metrica {
  align-self: flex-start;
  display: flex;
  gap: 48px;
  padding: 24px 32px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(82, 89, 78, 0.3);
  border-radius: var(--radius-lg);
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -2px rgba(0, 0, 0, 0.1);
}

.apresentacao__metrica-rotulo {
  padding-bottom: 4px;
  font-size: 12px;
  font-weight: 700;
  line-height: 16px;
  text-transform: uppercase;
  color: #2c3228;
}

.apresentacao__metrica-valor {
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 800;
  line-height: 52.8px;
  letter-spacing: -0.96px;
  color: var(--color-text);
}

.apresentacao__metrica-unidade {
  font-size: 24px;
  font-weight: 700;
  line-height: 31.2px;
  letter-spacing: 0;
  color: #2c3228;
}

.apresentacao__metrica-divisor {
  width: 1px;
  background: rgba(82, 89, 78, 0.4);
}

.apresentacao__canvas {
  position: relative;
  height: 420px;
}

.apresentacao__rodape {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 32px 16px 0;
}

.apresentacao__status {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 700;
  line-height: 19.6px;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: var(--color-text);
}

.apresentacao__ponto {
  width: 16px;
  height: 16px;
  border-radius: 9999px;
  background: #0a2408;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.apresentacao__controles {
  display: flex;
  gap: 16px;
}

.apresentacao__seta {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border: 1px solid rgba(82, 89, 78, 0.3);
  border-radius: 9999px;
  background: #e6e9e4;
  color: var(--color-text);
  filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.05));
}

.apresentacao__erro {
  margin-bottom: 16px;
  padding: 12px 16px;
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-sm);
  color: var(--color-danger);
}

@media (max-width: 900px) {
  .apresentacao {
    padding: 24px 16px 32px;
  }

  .apresentacao__titulo {
    font-size: 36px;
    line-height: 44px;
  }

  .apresentacao__grafico {
    padding: 24px 16px 16px;
  }
}
</style>
