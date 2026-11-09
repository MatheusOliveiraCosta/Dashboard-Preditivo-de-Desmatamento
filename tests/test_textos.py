from pipeline import estatistica, textos
from app.services import indicadores


def metricas_visao():
    return {"nome": "Pará", "ano_inicial": 2004, "ano": 2023, "area_km2": 3272.4,
            "ano_anterior": 2022, "area_anterior": 4141.0, "variacao_pct": -20.98,
            "ano_min": 2012, "area_min": 1741.0, "ano_max": 2004, "area_max": 8870.0}


def test_formatacao_ptbr():
    assert textos.fmt_int(9001) == "9.001"
    assert textos.fmt_int(1234567.4) == "1.234.567"
    assert textos.fmt_dec(22.44) == "22,4"
    assert textos.fmt_dec(0.5, 2) == "0,50"


def test_texto_visao_geral_traz_so_numeros_do_calculo():
    t = textos.texto_visao_geral(metricas_visao())
    assert t.startswith("Pará: a área desmatada em 2023 foi de 3.272 km²")
    assert "uma queda de 21,0% em relação a 2022 (4.141 km²)" in t
    assert "o menor valor foi em 2012 (1.741 km²) e o maior em 2004 (8.870 km²)" in t


def test_texto_visao_geral_sem_ano_anterior_ou_estavel():
    m = metricas_visao() | {"ano_anterior": None, "area_anterior": None, "variacao_pct": None}
    assert "queda" not in textos.texto_visao_geral(m)
    m = metricas_visao() | {"variacao_pct": 0.0}
    assert "praticamente igual a 2022" in textos.texto_visao_geral(m)


def test_texto_correlacao_e_projecao():
    c = textos.texto_correlacao({"nome": "Brasil", "ano_inicial": 2014, "ano_final": 2023, "r_temp": -0.07,
                                 "r_prec": None, "anomalia_c": 0.64, "deficit_mm": -276.3})
    assert "foi de -0,07" in c and "não pôde ser calculada" in c
    assert "0,6 °C acima" in c and "276 mm abaixo" in c
    p = textos.texto_projecao({"nome": "Brasil", "ano_base": 2023, "base_km2": 9001, "ano_final": 2030,
                               "final_km2": 7300, "inferior": 4100, "superior": 10500,
                               "variacao_pct": -18.9, "estabilizacao": 2028})
    assert "cerca de 7.300 km² em 2030, uma queda de 18,9% em relação a 2023 (9.001 km²)" in p
    assert "margem de incerteza entre 4.100 e 10.500 km²" in p and "estabilização a partir de 2028" in p


def test_llm_so_e_aceito_se_nao_inventar_numeros():
    m = metricas_visao()
    base = textos.texto_visao_geral(m)
    # reescrita fiel (mesmos números): aceita
    fiel, usou = textos.gerar_texto("VISAO_GERAL", m, lambda t: "Em 2023 o Pará perdeu 3.272 km² de floresta, 21,0% a menos que em 2022 (4.141 km²).")
    assert usou and fiel.startswith("Em 2023")
    # número novo (inventado): descartado, volta ao template
    inventado, usou = textos.gerar_texto("VISAO_GERAL", m, lambda t: "O desmatamento caiu 35% em 2023.")
    assert not usou and inventado == base
    # LLM fora do ar: volta ao template
    def quebra(_):
        raise RuntimeError("cota excedida")
    assert textos.gerar_texto("VISAO_GERAL", m, quebra) == (base, False)
    # resposta vazia
    assert textos.gerar_texto("VISAO_GERAL", m, lambda t: None) == (base, False)


def test_indicadores_da_api_e_do_etl_sao_iguais():
    x = [5012, 6207, 7893, 6947, 7536, 10129, 10851, 13038, 11594, 9001]
    y = [26.3, 26.9, 27.1, 26.5, 26.4, 26.7, 26.6, 26.4, 26.5, 27.3]
    assert indicadores.correlacao(x, y) == estatistica.correlacao(x, y)
    assert indicadores.taxa_supressao_pct(x) == estatistica.taxa_supressao_pct(x)
    assert indicadores.desvio_da_media(y) == estatistica.desvio_da_media(y)
    assert indicadores.variacao_percentual(9001, 11594) == estatistica.variacao_percentual(9001, 11594)


def test_indicadores_casos_limite():
    assert indicadores.correlacao([1, 2], [1, 2]) is None            # poucos pontos
    assert indicadores.correlacao([1, 1, 1], [1, 2, 3]) is None      # sem variação
    assert indicadores.variacao_percentual(5, 0) is None and indicadores.variacao_percentual(5, None) is None
    assert indicadores.taxa_supressao_pct([10]) is None
    assert round(indicadores.taxa_supressao_pct([100, 110, 99]), 1) == 0.0  # +10% e -10%
    assert indicadores.desvio_da_media([1, 2, 6]) == 3
