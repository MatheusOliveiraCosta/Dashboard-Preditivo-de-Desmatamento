"""Textos de insight (RF18). O número sempre vem do cálculo; o texto só o descreve.

Por padrão os textos saem de templates (determinísticos). Se houver chave do Gemini,
o template pode ser reescrito em linguagem mais natural, mas a versão do LLM só é
aceita se NÃO contiver nenhum número que não esteja no template: o LLM não calcula
nem inventa dados.
"""
import re

SYSTEM_PROMPT = (
    "Você é o redator científico do EcoMonitor Brasil, um painel educacional sobre "
    "desmatamento e clima voltado a estudantes e público geral.\n"
    "Regras obrigatórias:\n"
    "- Escreva em português do Brasil claro, direto e didático, em um único parágrafo "
    "com no máximo 3 frases.\n"
    "- NÃO use markdown, listas, títulos ou aspas envolvendo o texto.\n"
    "- NÃO altere, não arredonde, não remova e não acrescente nenhum número, ano, "
    "percentual ou unidade; copie exatamente os valores já formatados no contexto.\n"
    "- NÃO invente causas externas ou fatores não citados nos dados.\n"
    "- Responda apenas com o texto final reescrito."
)

OBJETIVO_TELA = {
    "VISAO_GERAL": "Resumir o desmatamento mais recente, a variação anual e os extremos históricos da localidade.",
    "CORRELACAO_CLIMATICA": "Explicar de forma acessível a relação estatística entre desmatamento, temperatura e chuva no período.",
    "PROJECAO_TENDENCIA": "Explicar a tendência projetada, a margem de incerteza e eventual estabilização sem tratar a projeção como certeza.",
}

PROMPT_REESCRITA = (
    "Contexto estruturado:\n{contexto}\n\n"
    "Texto-base (use exatamente estes números e fatos):\n{texto}"
)


def fmt_int(valor) -> str:
    return f"{round(valor):,}".replace(",", ".")


def fmt_dec(valor, casas=1) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def _mudanca(variacao):
    if abs(variacao) < 0.05:
        return None
    return "uma queda" if variacao < 0 else "um aumento"


def texto_visao_geral(m) -> str:
    texto = f"{m['nome']}: a área desmatada em {m['ano']} foi de {fmt_int(m['area_km2'])} km²"
    v = m.get("variacao_pct")
    if v is not None and m.get("ano_anterior") is not None:
        mudanca = _mudanca(v)
        ref = f"{m['ano_anterior']} ({fmt_int(m['area_anterior'])} km²)"
        texto += (f", {mudanca} de {fmt_dec(abs(v))}% em relação a {ref}." if mudanca
                  else f", praticamente igual a {ref}.")
    else:
        texto += "."
    if m["ano_min"] != m["ano_max"]:
        texto += (f" Na série de {m['ano_inicial']} a {m['ano']}, o menor valor foi em "
                  f"{m['ano_min']} ({fmt_int(m['area_min'])} km²) e o maior em "
                  f"{m['ano_max']} ({fmt_int(m['area_max'])} km²).")
    return texto


def texto_correlacao(m) -> str:
    def trecho(r, rotulo):
        return f"{rotulo} foi de {fmt_dec(r, 2)}" if r is not None else f"{rotulo} não pôde ser calculada"

    temp = trecho(m.get("r_temp"), "a correlação entre o desmatamento e a temperatura média")
    chuva = trecho(m.get("r_prec"), "entre o desmatamento e a precipitação")
    t_dir = "acima" if m["anomalia_c"] >= 0 else "abaixo"
    p_dir = "acima" if m["deficit_mm"] >= 0 else "abaixo"
    return (f"{m['nome']}: entre {m['ano_inicial']} e {m['ano_final']}, {temp} e {chuva}. "
            f"Em {m['ano_final']}, a temperatura média ficou {fmt_dec(abs(m['anomalia_c']))} °C "
            f"{t_dir} da média do período e a chuva total, {fmt_int(abs(m['deficit_mm']))} mm "
            f"{p_dir} dela.")


def texto_projecao(m) -> str:
    mudanca = _mudanca(m["variacao_pct"])
    base = f"{m['ano_base']} ({fmt_int(m['base_km2'])} km²)"
    comparacao = (f"{mudanca} de {fmt_dec(abs(m['variacao_pct']))}% em relação a {base}" if mudanca
                  else f"praticamente igual a {base}")
    texto = (f"{m['nome']}: se a tendência atual continuar, a área desmatada deve chegar a cerca "
             f"de {fmt_int(m['final_km2'])} km² em {m['ano_final']}, {comparacao}, com margem de "
             f"incerteza entre {fmt_int(m['inferior'])} e {fmt_int(m['superior'])} km².")
    if m.get("estabilizacao"):
        texto += f" O modelo indica estabilização a partir de {m['estabilizacao']}."
    return texto


TEMPLATES = {
    "VISAO_GERAL": texto_visao_geral,
    "CORRELACAO_CLIMATICA": texto_correlacao,
    "PROJECAO_TENDENCIA": texto_projecao,
}


def _contexto_estruturado(tela, m) -> str:
    linhas = [
        f"- Tela: {tela}",
        f"- Objetivo: {OBJETIVO_TELA.get(tela, '')}",
        f"- Localidade: {m['nome']}",
    ]
    if tela == "VISAO_GERAL":
        linhas.append(f"- Ano de referência: {m['ano']} ({fmt_int(m['area_km2'])} km²)")
        v = m.get("variacao_pct")
        if v is not None and m.get("ano_anterior") is not None:
            mudanca = _mudanca(v)
            detalhe = f"{mudanca} de {fmt_dec(abs(v))}%" if mudanca else "estável"
            linhas.append(
                f"- Comparação com {m['ano_anterior']} ({fmt_int(m['area_anterior'])} km²): {detalhe}"
            )
        if m["ano_min"] != m["ano_max"]:
            linhas.append(
                f"- Extremos ({m['ano_inicial']}–{m['ano']}): menor em {m['ano_min']} "
                f"({fmt_int(m['area_min'])} km²), maior em {m['ano_max']} ({fmt_int(m['area_max'])} km²)"
            )
    elif tela == "CORRELACAO_CLIMATICA":
        linhas.append(f"- Período: {m['ano_inicial']} a {m['ano_final']}")
        r_t = fmt_dec(m["r_temp"], 2) if m.get("r_temp") is not None else "não calculada"
        r_p = fmt_dec(m["r_prec"], 2) if m.get("r_prec") is not None else "não calculada"
        linhas.append(f"- Correlação (r): temperatura = {r_t}; precipitação = {r_p}")
        t_dir = "acima" if m["anomalia_c"] >= 0 else "abaixo"
        p_dir = "acima" if m["deficit_mm"] >= 0 else "abaixo"
        linhas.append(
            f"- Desvio em {m['ano_final']}: {fmt_dec(abs(m['anomalia_c']))} °C {t_dir} da média; "
            f"{fmt_int(abs(m['deficit_mm']))} mm {p_dir} da média"
        )
    elif tela == "PROJECAO_TENDENCIA":
        mudanca = _mudanca(m["variacao_pct"])
        detalhe = f"{mudanca} de {fmt_dec(abs(m['variacao_pct']))}%" if mudanca else "estável"
        linhas.append(f"- Ano-base: {m['ano_base']} ({fmt_int(m['base_km2'])} km²)")
        linhas.append(
            f"- Projeção para {m['ano_final']}: {fmt_int(m['final_km2'])} km² ({detalhe}); "
            f"incerteza entre {fmt_int(m['inferior'])} e {fmt_int(m['superior'])} km²"
        )
        if m.get("estabilizacao"):
            linhas.append(f"- Estabilização estimada: a partir de {m['estabilizacao']}")
    return "\n".join(linhas)


_NUMEROS = re.compile(r"\d+(?:[.,]\d+)*")


def _numeros(texto):
    return {n.rstrip(".,") for n in _NUMEROS.findall(texto)}


def validar_numeros(original, reescrito) -> bool:
    """True se o texto reescrito não traz número que não estivesse no original."""
    return _numeros(reescrito) <= _numeros(original)


def gerar_texto(tela, metricas, reescritor=None):
    """Devolve (texto, usou_llm)."""
    base = TEMPLATES[tela](metricas)
    if reescritor is None:
        return base, False
    try:
        if getattr(reescritor, "_aceita_contexto", False):
            novo = reescritor(base, tela=tela, metricas=metricas)
        else:
            novo = reescritor(base)
    except Exception as erro:  # qualquer falha do LLM cai no template
        print(f"  [insights] LLM falhou ({erro}); usando o template.")
        return base, False
    novo = (novo or "").strip()
    if novo and len(novo) <= 700 and validar_numeros(base, novo):
        return novo, True
    if novo:
        print("  [insights] texto do LLM descartado (números diferentes do cálculo); usando o template.")
    return base, False


def criar_reescritor_gemini(api_key, modelo):
    """Reescritor que chama o Gemini. Importa o SDK só se for usado."""
    from google import genai
    from google.genai import types

    cliente = genai.Client(api_key=api_key)
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.3,
        max_output_tokens=300,
    )

    def reescrever(texto, tela=None, metricas=None):
        if tela and metricas:
            conteudo = PROMPT_REESCRITA.format(
                contexto=_contexto_estruturado(tela, metricas),
                texto=texto,
            )
        else:
            conteudo = f"Texto-base:\n{texto}"
        resposta = cliente.models.generate_content(
            model=modelo,
            contents=conteudo,
            config=cfg,
        )
        return resposta.text

    reescrever._aceita_contexto = True
    return reescrever