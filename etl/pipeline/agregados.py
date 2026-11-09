"""Brasil = agregação das outras localidades (nenhuma fonte entrega o país pronto).

* Desmatamento: soma dos BIOMAS (os biomas cobrem o país sem sobreposição). Somar estados
  e biomas juntos contaria a mesma área duas vezes.
* Clima: média dos ESTADOS, só nos anos com pelo menos MIN_ESTADOS_BRASIL estados.
"""
from . import config


def _brasil_id(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM localidade WHERE tipo = 'PAIS'")
        linha = cur.fetchone()
    if not linha:
        raise RuntimeError("Registro 'Brasil' não existe. Rode a etapa de localidades (seed).")
    return linha[0]


def _desmatamento(conn, brasil_id):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT d.fonte, d.ano, SUM(d.area_km2), COUNT(DISTINCT d.localidade_id)
               FROM desmatamento_anual d JOIN localidade l ON l.id = d.localidade_id
               WHERE l.tipo = 'BIOMA'
               GROUP BY d.fonte, d.ano ORDER BY d.fonte, d.ano"""
        )
        linhas = cur.fetchall()

    por_fonte = {}
    for fonte, ano, total, n in linhas:
        por_fonte.setdefault(fonte, []).append((ano, total, n))

    inseridos = 0
    with conn.cursor() as cur:
        for fonte, anos in por_fonte.items():
            n_biomas = max(n for _, _, n in anos)
            if n_biomas < 6:
                print(f"  [agregados] AVISO: o Brasil de {fonte} soma só {n_biomas} de 6 biomas; "
                      f"carregue os 6 para o total nacional ficar completo.")
            # só os anos em que todos os biomas disponíveis da fonte têm dado
            validos = [(ano, total) for ano, total, n in anos if n == n_biomas]
            cur.execute("DELETE FROM desmatamento_anual WHERE localidade_id = %s AND fonte = %s",
                        (brasil_id, fonte))
            for ano, total in validos:
                cur.execute(
                    "INSERT INTO desmatamento_anual (localidade_id, ano, area_km2, fonte) "
                    "VALUES (%s, %s, %s, %s)", (brasil_id, ano, float(total), fonte))
                inseridos += 1
    return inseridos


def _clima(conn, brasil_id):
    with conn.cursor() as cur:
        cur.execute(
            """SELECT c.ano, AVG(c.temperatura_media_c), AVG(c.precipitacao_mm), COUNT(*)
               FROM dado_climatico c JOIN localidade l ON l.id = c.localidade_id
               WHERE l.tipo = 'ESTADO'
                 AND c.temperatura_media_c IS NOT NULL AND c.precipitacao_mm IS NOT NULL
               GROUP BY c.ano HAVING COUNT(*) >= %s ORDER BY c.ano""",
            (config.MIN_ESTADOS_BRASIL,),
        )
        linhas = cur.fetchall()
        cur.execute("DELETE FROM dado_climatico WHERE localidade_id = %s", (brasil_id,))
        for ano, temp, prec, _ in linhas:
            cur.execute(
                "INSERT INTO dado_climatico (localidade_id, ano, temperatura_media_c, "
                "precipitacao_mm, fonte) VALUES (%s, %s, %s, %s, 'INMET')",
                (brasil_id, ano, round(float(temp), 2), round(float(prec), 1)))
    if not linhas:
        print(f"  [agregados] clima do Brasil: nenhum ano com {config.MIN_ESTADOS_BRASIL}+ estados")
    return len(linhas)


def executar(conn):
    brasil_id = _brasil_id(conn)
    return _desmatamento(conn, brasil_id) + _clima(conn, brasil_id)
