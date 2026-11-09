import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # etl/ (no container: /app)
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ecomonitor"
)

# Local: <raiz do repo>/data/raw. No container: /data/raw (volume ./data:/data).
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR.parent / "data"))
RAW_DIR = DATA_DIR / "raw"
PRODES_ESTADOS = RAW_DIR / "prodes" / "prodes_estados.csv"
PRODES_BIOMAS = RAW_DIR / "prodes" / "prodes_biomas.csv"
MAPBIOMAS_ESTADOS = RAW_DIR / "mapbiomas" / "mapbiomas_estados.csv"
MAPBIOMAS_BIOMAS = RAW_DIR / "mapbiomas" / "mapbiomas_biomas.csv"
INMET_DIR = RAW_DIR / "inmet"
INMET_ESTACOES_BIOMA = INMET_DIR / "estacoes_bioma.csv"

# Primeiro ano carregado no banco
ANO_MIN = 2004

# Último ano carregado. O ano PRODES corrente ainda é parcial (a taxa só é
# consolidada meses depois), então fica de fora para não distorcer o modelo.
ANO_MAX = 2026

# Unidade dos valores do arquivo do MapBiomas: "ha" ou "km2"
MAPBIOMAS_UNIDADE = "ha"

# True: ano do clima = ano PRODES (agosto do ano anterior a julho do ano).
# False: ano civil.
CLIMA_ANO_PRODES = True

# Fração mínima das 8760 horas do ano com dado para a estação-ano valer
CLIMA_COBERTURA_MIN = 0.8

# ---------------------------------------------------------------------------
# Brasil, projeção e textos de insight
# ---------------------------------------------------------------------------
PROCESSED_DIR = DATA_DIR / "processed"

# O "Brasil" do clima é a média dos estados; só vale no ano com pelo menos este
# número de estados com dado (nos anos iniciais o INMET tem poucas estações).
MIN_ESTADOS_BRASIL = int(os.getenv("MIN_ESTADOS_BRASIL", "20"))

# Modelo de projeção (regressão linear sobre o tempo)
ANOS_PROJECAO = int(os.getenv("ANOS_PROJECAO", "7"))   # anos à frente
JANELA_MODELO = int(os.getenv("JANELA_MODELO", "15"))  # usa só os últimos N anos
MIN_ANOS_MODELO = int(os.getenv("MIN_ANOS_MODELO", "8"))  # mínimo de anos para projetar

# Reescrita opcional dos textos com Gemini. Sem chave E modelo, usa só o template.
# O nome do modelo muda com o tempo: confira o atual em https://ai.google.dev/gemini-api/docs/models
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or None
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or None
USAR_LLM = True  # run_etl.py coloca False com --sem-llm
