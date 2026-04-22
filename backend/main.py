"""Fleet&Brick ERP - FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import veiculos, tickets
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação."""
    # Startup
    print("🚀 Fleet&Brick ERP iniciando...")
    yield
    # Shutdown
    print("🛑 Fleet&Brick ERP encerrando...")


app = FastAPI(
    title="Fleet&Brick ERP API",
    description="API unificada para gestão de frotas e imobiliária",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://app.fleetbrick.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(veiculos.router, prefix="/api", tags=["Veículos"])
app.include_router(tickets.router, prefix="/api", tags=["Suporte"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fleetbrick-api", "version": "1.0.0"}


@app.get("/")
async def root():
    return {
        "message": "Fleet&Brick ERP API",
        "docs": "/docs",
        "health": "/health"
    }
