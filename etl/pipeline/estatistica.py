"""Funções estatísticas simples usadas nos textos de insight.

As mesmas fórmulas existem em backend/app/services/indicadores.py (a API calcula os
indicadores na hora, respeitando o período pedido). Mantenha as duas em sincronia.
"""
import statistics
from collections.abc import Sequence


def variacao_percentual(atual, anterior):
    if anterior is None or anterior == 0:
        return None
    return (atual - anterior) / anterior * 100


def taxa_supressao_pct(areas: Sequence[float], ultimos_anos: int = 10):
    """Média das variações anuais (%) nos últimos anos da série."""
    janela = list(areas)[-(ultimos_anos + 1):]
    variacoes = [v for a, b in zip(janela, janela[1:])
                 if (v := variacao_percentual(b, a)) is not None]
    return statistics.fmean(variacoes) if variacoes else None


def correlacao(x: Sequence[float], y: Sequence[float]):
    """Pearson; None com menos de 3 pontos ou sem variação em uma das séries."""
    if len(x) != len(y) or len(x) < 3:
        return None
    if statistics.pstdev(x) == 0 or statistics.pstdev(y) == 0:
        return None
    return statistics.correlation(x, y)


def desvio_da_media(valores: Sequence[float]) -> float:
    """Último valor menos a média da série (anomalia térmica e déficit hídrico)."""
    return valores[-1] - statistics.fmean(valores)
