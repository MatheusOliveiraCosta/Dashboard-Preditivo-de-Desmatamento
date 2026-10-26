from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.db import query
from app.routers import climate, localidades, overview, projection

app = FastAPI(
    title="EcoMonitor API",
    description="Contrato em docs/arquitetura-contrato-api.md. "
                "ATENÇÃO: os dados ainda são MOCK (fictícios).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def marcar_dados_mock(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Data-Source"] = "mock"
    return response


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
