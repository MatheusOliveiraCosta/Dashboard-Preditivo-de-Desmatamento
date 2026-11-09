"""Testes de ponta a ponta: schema real do projeto em um PostgreSQL de teste.

Defina TEST_DATABASE_URL apontando para um servidor PostgreSQL (o banco informado na URL
é APAGADO e recriado a cada execução). Exemplo com o docker compose do projeto:

    TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecomonitor_test pytest
"""
import os
from pathlib import Path

import psycopg2
import pytest
from psycopg2.extensions import make_dsn, parse_dsn

RAIZ = Path(__file__).resolve().parents[1]
TEST_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ecomonitor_test")
TABELAS = "localidade, desmatamento_anual, dado_climatico, projecao, insight, status_sistema"


@pytest.fixture(scope="session")
def banco():
    dsn = parse_dsn(TEST_URL)
    nome = dsn["dbname"]
    admin = psycopg2.connect(make_dsn(**{**dsn, "dbname": "postgres"}))
    admin.autocommit = True
    with admin.cursor() as cur:
        cur.execute(f'DROP DATABASE IF EXISTS "{nome}" WITH (FORCE)')
        cur.execute(f'CREATE DATABASE "{nome}"')
    admin.close()

    conn = psycopg2.connect(TEST_URL)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute((RAIZ / "database" / "schema.sql").read_text(encoding="utf-8"))
    conn.close()

    os.environ["DATABASE_URL"] = TEST_URL  # usado pelo backend
    return TEST_URL


@pytest.fixture
def conn(banco):
    c = psycopg2.connect(banco)
    with c.cursor() as cur:
        cur.execute(f"TRUNCATE {TABELAS} RESTART IDENTITY CASCADE")
    c.commit()
    yield c
    c.close()
