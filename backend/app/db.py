import os

import psycopg2
from psycopg2.extras import RealDictCursor


def query(sql: str, params: tuple = ()):
    """Executa um SELECT e devolve lista de dicts.

    Conexão por requisição: simples e suficiente para o MVP.
    """
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()
