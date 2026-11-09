import pytest

from pipeline import modelo


def test_reta_perfeita_e_projetada_exatamente():
    anos = list(range(2010, 2020))
    valores = [100 + 10 * (a - 2010) for a in anos]
    pontos = modelo.projetar(anos, valores, horizonte=3)
    assert [p.ano for p in pontos] == [2020, 2021, 2022]
    assert [round(p.valor) for p in pontos] == [200, 210, 220]
    # sem ruído, não há incerteza
    assert all(p.inferior == pytest.approx(p.valor) and p.superior == pytest.approx(p.valor) for p in pontos)


def test_intervalo_contem_o_valor_e_abre_com_o_horizonte():
    anos = list(range(2005, 2024))
    valores = [5000 - 120 * (a - 2005) + (400 if a % 3 == 0 else -250) for a in anos]
    pontos = modelo.projetar(anos, valores, horizonte=7)
    for p in pontos:
        assert 0 <= p.inferior <= p.valor <= p.superior
    larguras = [p.superior - p.inferior for p in pontos]
    assert larguras == sorted(larguras) and larguras[-1] > larguras[0]


def test_projecao_nunca_e_negativa():
    anos = list(range(2010, 2020))
    valores = [100 - 12 * (a - 2010) for a in anos]  # cai abaixo de zero em ~2018
    pontos = modelo.projetar(anos, valores, horizonte=5)
    assert all(p.valor >= 0 and p.inferior >= 0 for p in pontos)
    assert pontos[-1].valor == 0


def test_janela_usa_so_os_ultimos_anos():
    anos = list(range(2000, 2020))
    valores = [1000] * 10 + [100 + 10 * (a - 2010) for a in range(2010, 2020)]
    pontos = modelo.projetar(anos, valores, horizonte=1, janela=10)
    assert round(pontos[0].valor) == 200  # ignora o patamar antigo de 1000


def test_exige_ao_menos_tres_anos():
    with pytest.raises(ValueError):
        modelo.projetar([2022, 2023], [10, 11], horizonte=2)


def test_avaliacao_de_reta_perfeita_tem_erro_zero():
    anos = list(range(2005, 2024))
    valores = [200 + 5 * (a - 2005) for a in anos]
    m = modelo.avaliar(anos, valores)
    assert m["n_teste"] == 3
    assert m["mae"] == pytest.approx(0, abs=1e-6) and m["rmse"] == pytest.approx(0, abs=1e-6)


def test_avaliacao_sem_historico_suficiente():
    assert modelo.avaliar([2020, 2021, 2022], [1, 2, 3])["n_teste"] == 0


def test_ponto_de_estabilizacao():
    # variações de -10%, -5%, -0,5%: estabiliza no 3º ano projetado
    proj = [(2024, 90.0), (2025, 85.5), (2026, 85.0725), (2027, 80.0)]
    assert modelo.ponto_estabilizacao(100.0, proj) == 2026
    assert modelo.ponto_estabilizacao(100.0, [(2024, 90.0), (2025, 80.0)]) is None
