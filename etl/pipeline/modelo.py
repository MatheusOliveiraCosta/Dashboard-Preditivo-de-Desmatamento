"""Projeção de tendência (RF09/RF10): regressão linear sobre o tempo com intervalo de 95%.

A tendência vem do scikit-learn (LinearRegression); a margem de incerteza usa a fórmula
clássica do intervalo de previsão da regressão linear simples. É uma estimativa
estatística de tendência, não uma previsão determinística.
"""
import json
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
from psycopg2.extras import execute_values
from scipy import stats
from sklearn.linear_model import LinearRegression

from . import config, consultas


@dataclass(frozen=True)
class Ponto:
    ano: int
    valor: float
    inferior: float
    superior: float


def projetar(anos, valores, horizonte, janela=15, nivel=0.95):
    """Projeta os próximos `horizonte` anos a partir dos últimos `janela` anos da série."""
    x = np.asarray(anos[-janela:], dtype=float)
    y = np.asarray(valores[-janela:], dtype=float)
    n = len(x)
    if n < 3:
        raise ValueError("São necessários ao menos 3 anos de dados para projetar.")

    modelo = LinearRegression().fit(x.reshape(-1, 1), y)
    residuos = y - modelo.predict(x.reshape(-1, 1))
    erro_padrao = float(np.sqrt(np.sum(residuos ** 2) / (n - 2)))
    sxx = float(np.sum((x - x.mean()) ** 2))
    t_critico = float(stats.t.ppf(1 - (1 - nivel) / 2, n - 2))

    futuros = np.arange(x[-1] + 1, x[-1] + horizonte + 1)
    previsto = modelo.predict(futuros.reshape(-1, 1))
    margem = t_critico * erro_padrao * np.sqrt(1 + 1 / n + (futuros - x.mean()) ** 2 / sxx)

    pontos = []
    for ano, p, m in zip(futuros, previsto, margem):
        valor = max(0.0, float(p))  # área desmatada não pode ser negativa
        inferior = min(valor, max(0.0, float(p - m)))
        superior = max(valor, float(p + m))
        pontos.append(Ponto(int(ano), valor, inferior, superior))
    return pontos


def avaliar(anos, valores, janela=15, n_teste=3, min_treino=5):
    """Validação nos últimos anos: ajusta com o passado e prevê o ano seguinte, ano a ano."""
    reais, previstos = [], []
    for i in range(max(min_treino, len(valores) - n_teste), len(valores)):
        previstos.append(projetar(anos[:i], valores[:i], 1, janela)[0].valor)
        reais.append(float(valores[i]))
    if not reais:
        return {"n_teste": 0, "mae": None, "rmse": None, "r2": None}
    r, p = np.asarray(reais), np.asarray(previstos)
    erro = r - p
    ss_tot = float(np.sum((r - r.mean()) ** 2))
    return {
        "n_teste": len(reais),
        "mae": float(np.mean(np.abs(erro))),
        "rmse": float(np.sqrt(np.mean(erro ** 2))),
        "r2": float(1 - np.sum(erro ** 2) / ss_tot) if len(r) >= 2 and ss_tot > 0 else None,
    }


def ponto_estabilizacao(base, projecao, limite_pct=1.0):
    """Primeiro ano projetado cuja variação anual (em módulo) fica abaixo de `limite_pct`.

    CRITÉRIO PROVISÓRIO: a definição de "Ponto de Estabilização" ainda precisa ser
    validada com a equipe de Dados/IA.
    """
    anterior = base
    for ano, valor in projecao:
        if anterior > 0 and abs((valor - anterior) / anterior * 100) < limite_pct:
            return ano
        anterior = valor
    return None


def executar(conn):
    nomes = consultas.localidades(conn)
    series = consultas.series_desmatamento(conn)
    metricas, total = {}, 0

    with conn.cursor() as cur:
        for loc_id, s in sorted(series.items()):
            nome = nomes[loc_id]["nome"]
            if len(s["anos"]) < config.MIN_ANOS_MODELO:
                print(f"  [projecao] {nome}: só {len(s['anos'])} anos de dados "
                      f"(mínimo {config.MIN_ANOS_MODELO}); sem projeção")
                continue
            pontos = projetar(s["anos"], s["valores"], config.ANOS_PROJECAO, config.JANELA_MODELO)
            ano_base = s["anos"][-1]
            cur.execute("DELETE FROM projecao WHERE localidade_id = %s", (loc_id,))
            execute_values(
                cur,
                "INSERT INTO projecao (localidade_id, ano_base, ano_projetado, valor_projetado_km2, "
                "intervalo_inferior, intervalo_superior) VALUES %s",
                [(loc_id, ano_base, p.ano, p.valor, p.inferior, p.superior) for p in pontos],
            )
            total += len(pontos)
            metricas[nome] = {"fonte": s["fonte"], "ano_base": ano_base,
                              **avaliar(s["anos"], s["valores"], config.JANELA_MODELO)}

    # Métricas de validação (MAE, RMSE, R²) para consulta e para o capítulo de metodologia
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    saida = config.PROCESSED_DIR / "metricas_modelo.json"
    saida.write_text(json.dumps({
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "modelo": "LinearRegression (scikit-learn) sobre o ano; intervalo de previsão de 95%",
        "janela_anos": config.JANELA_MODELO, "anos_projetados": config.ANOS_PROJECAO,
        "localidades": metricas}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [projecao] métricas de validação em {saida}")
    return total
