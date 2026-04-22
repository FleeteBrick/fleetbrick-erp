"""Schemas Pydantic para validação de dados"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# Planos
class PlanoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50)
    descricao: Optional[str] = None
    preco: Decimal = Field(..., ge=0)
    max_veiculos: int = Field(..., ge=0)
    max_imoveis: int = Field(..., ge=0)
    max_usuarios: int = Field(..., ge=0)
    recursos: List[str] = Field(default_factory=list)
    ativo: bool = True

class PlanoCreate(PlanoBase):
    pass

class PlanoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco: Optional[Decimal] = None
    max_veiculos: Optional[int] = None
    max_imoveis: Optional[int] = None
    max_usuarios: Optional[int] = None
    recursos: Optional[List[str]] = None
    ativo: Optional[bool] = None

class PlanoResponse(PlanoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Veículos
class VeiculoBase(BaseModel):
    placa: str = Field(..., min_length=7, max_length=10)
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano: Optional[int] = Field(None, ge=1900, le=2100)
    cor: Optional[str] = None
    tipo: Optional[str] = None
    status: str = "ativo"
    quilometragem_atual: int = Field(default=0, ge=0)
    custo_mensal_estimado: Optional[Decimal] = None
    documentos: Dict[str, Any] = Field(default_factory=dict)

class VeiculoCreate(VeiculoBase):
    pass

class VeiculoUpdate(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    ano: Optional[int] = None
    cor: Optional[str] = None
    status: Optional[str] = None
    quilometragem_atual: Optional[int] = None
    data_proxima_manutencao: Optional[datetime] = None
    custo_mensal_estimado: Optional[Decimal] = None

class VeiculoResponse(VeiculoBase):
    id: UUID
    empresa_id: UUID
    data_ultima_manutencao: Optional[datetime] = None
    data_proxima_manutencao: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tickets
class TicketBase(BaseModel):
    tipo: str = Field(..., pattern="^(suporte|bug|feedback|sugestao)$")
    categoria: Optional[str] = "outro"
    prioridade: str = "media"
    titulo: str = Field(..., min_length=5, max_length=255)
    descricao: str = Field(..., min_length=10)

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    resposta_staff: Optional[str] = None
    prioridade: Optional[str] = None
    satisfacao: Optional[int] = Field(None, ge=1, le=5)

class TicketResponse(TicketBase):
    id: UUID
    empresa_id: Optional[UUID] = None
    usuario_id: Optional[UUID] = None
    status: str
    resposta_staff: Optional[str] = None
    resolvido_por: Optional[UUID] = None
    data_resolucao: Optional[datetime] = None
    satisfacao: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Auth
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    nome: str = Field(..., min_length=2, max_length=255)
    empresa_nome: str = Field(..., min_length=2, max_length=255)
    plano_id: UUID

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]
