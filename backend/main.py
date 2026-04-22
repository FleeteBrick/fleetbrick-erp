"""Fleet&Brick ERP - FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import veiculos, propriedades, webhooks, support, contratos, pagamentos


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Fleet&Brick ERP iniciando...")
    yield
    print("🛑 Fleet&Brick ERP encerrando...")


app = FastAPI(
    title="Fleet&Brick ERP API",
    description="API unificada para gestão de frotas e imóveis",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(veiculos.router)
app.include_router(propriedades.router)
app.include_router(contratos.router)
app.include_router(pagamentos.router)
app.include_router(support.router)
app.include_router(webhooks.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fleetbrick-api", "version": "1.0.0"}


@app.get("/")
async def root():
    return {"message": "Fleet&Brick ERP API", "docs": "/docs", "health": "/health"}