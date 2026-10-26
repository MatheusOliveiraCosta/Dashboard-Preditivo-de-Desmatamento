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