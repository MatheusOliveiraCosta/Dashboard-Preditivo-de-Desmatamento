"""Gera e grava os textos de insight (RF18) de cada localidade e tela.

Guarda em insight.metricas_origem os números que originaram o texto (e, na projeção,
o ponto de estabilização), assim a API devolve o texto sem recalcular nada.
"""
import json

from . import config, consultas, estatistica, modelo, textos


def _reescritor():
    if not (config.USAR_LLM and config.GEMINI_API_KEY and config.GEMINI_MODEL):
        return None
    base = textos.criar_reescritor_gemini(config.GEMINI_API_KEY, config.GEMINI_MODEL)
    falhas = {"seguidas": 0}

    def resiliente(texto):
        if falhas["seguidas"] >= 3:  # desiste do LLM (cota/chave) e segue só com templates
            return None
        try:
            saida = base(texto)
            falhas["seguidas"] = 0
            return saida
        except Exception:
            falhas["seguidas"] += 1
            raise

    return resiliente


def _metricas_visao_geral(nome, s):
    anos, valores = s["anos"], s["valores"]
    ano, area = anos[-1], valores[-1]
    anterior = valores[-2] if len(anos) > 1 and anos[-2] == ano - 1 else None
    i_min = min(range(len(valores)), key=valores.__getitem__)
    i_max = max(range(len(valores)), key=valores.__getitem__)
    return {
        "nome": nome, "fonte": s["fonte"], "ano_inicial": anos[0], "ano": ano, "area_km2": area,
        "ano_anterior": ano - 1 if anterior is not None else None, "area_anterior": anterior,
        "variacao_pct": estatistica.variacao_percentual(area, anterior),
        "ano_min": anos[i_min], "area_min": valores[i_min],
        "ano_max": anos[i_max], "area_max": valores[i_max],
    }


def _metricas_correlacao(nome, s, clima):
    pares = [(a, v) for a, v in zip(s["anos"], s["valores"]) if a in clima]
    if len(pares) < 3:
        return None
    anos = [a for a, _ in pares]
    areas = [v for _, v in pares]
    temps = [clima[a][0] for a in anos]
    chuvas = [clima[a][1] for a in anos]
    return {
        "nome": nome, "ano_inicial": anos[0], "ano_final": anos[-1],
        "r_temp": estatistica.correlacao(areas, temps), "r_prec": estatistica.correlacao(areas, chuvas),
        "anomalia_c": estatistica.desvio_da_media(temps), "deficit_mm": estatistica.desvio_da_media(chuvas),
        "taxa_supressao_pct": estatistica.taxa_supressao_pct(areas),
    }


def _metricas_projecao(nome, s, pontos):
    if not pontos:
        return None
    base = s["valores"][-1]
    final = pontos[-1]
    return {
        "nome": nome, "ano_base": s["anos"][-1], "base_km2": base,
        "ano_final": final[0], "final_km2": final[1], "inferior": final[2], "superior": final[3],
        "variacao_pct": estatistica.variacao_percentual(final[1], base),
        "estabilizacao": modelo.ponto_estabilizacao(base, [(a, v) for a, v, _, _ in pontos]),
    }


def _gravar(cur, loc_id, tela, texto, metricas):
    cur.execute("DELETE FROM insight WHERE localidade_id = %s AND tela = %s", (loc_id, tela))
    cur.execute(
        "INSERT INTO insight (localidade_id, tela, texto_gerado, metricas_origem) "
        "VALUES (%s, %s, %s, %s)", (loc_id, tela, texto, json.dumps(metricas, default=float)))


def executar(conn):
    nomes = consultas.localidades(conn)
    series = consultas.series_desmatamento(conn)
    clima = consultas.series_clima(conn)
    reescritor = _reescritor()
    gravados, com_llm = 0, 0

    with conn.cursor() as cur:
        for loc_id, s in sorted(series.items()):
            nome = nomes[loc_id]["nome"]
            candidatos = {
                "VISAO_GERAL": _metricas_visao_geral(nome, s),
                "CORRELACAO_CLIMATICA": _metricas_correlacao(nome, s, clima.get(loc_id, {})),
                "PROJECAO_TENDENCIA": _metricas_projecao(nome, s, consultas.projecao_vigente(conn, loc_id)),
            }
            for tela, metricas in candidatos.items():
                if metricas is None:
                    continue
                texto, usou = textos.gerar_texto(tela, metricas, reescritor)
                _gravar(cur, loc_id, tela, texto, metricas)
                gravados += 1
                com_llm += usou
    if reescritor:
        print(f"  [insights] {com_llm} de {gravados} textos reescritos com o Gemini")
    return gravados
