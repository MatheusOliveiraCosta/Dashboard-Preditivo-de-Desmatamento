"""Textos de insight (RF18). O número sempre vem do cálculo; o texto só o descreve.

Por padrão os textos saem de templates (determinísticos). Se houver chave e modelo do
Gemini, o template pode ser reescrito em linguagem mais natural, mas a versão do LLM só
é aceita se NÃO contiver nenhum número que não esteja no template: o LLM não calcula
nem inventa dados.
"""
import re

PROMPT_REESCRITA = (
    "Reescreva o texto abaixo em português do Brasil, em linguagem simples para estudantes, "
    "com no máximo 3 frases. Não altere, não remova e não acrescente números, anos ou fatos. "
    "Responda apenas com o texto reescrito.\n\nTexto:\n{texto}"
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

    cliente = genai.Client(api_key=api_key)

    def reescrever(texto):
        resposta = cliente.models.generate_content(
            model=modelo, contents=PROMPT_REESCRITA.format(texto=texto))
        return resposta.text

    return reescrever
