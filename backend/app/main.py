import os

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EcoMonitor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # desenvolvimento; restringir no deploy
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Contrato: todos os endpoints ficam sob /api/v1
api = APIRouter(prefix="/api/v1")


def query(sql: str, params: tuple = ()):
    # Conexão por requisição: simples e suficiente para o MVP.
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


@api.get("/health")
def health():
    query("SELECT 1")
    return {"status": "ok"}


@api.get("/localidades")
def localidades():
    """Lista de estados/biomas para o filtro."""
    return query("SELECT * FROM localidade ORDER BY nome")


# TODO (próximos cards de backend), conforme docs/arquitetura-contrato-api.md:
#   GET /api/v1/overview?localidade=&ano_inicio=&ano_fim=
#   GET /api/v1/climate-correlation?localidade=&start=&end=
#   GET /api/v1/projection?localidade=&horizon=

app.include_router(api)
