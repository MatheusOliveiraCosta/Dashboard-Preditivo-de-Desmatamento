from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import query
from app.routers import climate, localidades, overview, projection

app = FastAPI(
    title="EcoMonitor API",
    description="API somente de leitura (sem autenticação). Dados: PRODES/INPE, MapBiomas e INMET, "
                "carregados pelo ETL. Contrato em docs/arquitetura-contrato-api.md.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


api = APIRouter(prefix="/api/v1")


@api.get("/health")
def health():
    query("SELECT 1")
    return {"status": "ok"}


api.include_router(localidades.router)
api.include_router(overview.router)
api.include_router(climate.router)
api.include_router(projection.router)
app.include_router(api)
