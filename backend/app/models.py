"""Modelos SQLAlchemy"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Numeric, JSON, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Plano(Base):
    __tablename__ = "planos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    descricao = Column(Text)
    preco = Column(Numeric(10, 2), nullable=False, default=197.00)
    max_veiculos = Column(Integer, nullable=False, default=5)
    max_imoveis = Column(Integer, nullable=False, default=10)
    max_usuarios = Column(Integer, nullable=False, default=3)
    recursos = Column(JSONB, default=list)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(18), unique=True)
    email = Column(String(255), nullable=False)
    telefone = Column(String(20))
    plano_id = Column(UUID(as_uuid=True), ForeignKey("planos.id"), nullable=False)
    asaas_customer_id = Column(String(100))
    asaas_subscription_id = Column(String(100))
    status_assinatura = Column(String(50), default="trial")
    data_vencimento_trial = Column(DateTime(timezone=True))
    configuracoes = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    telefone = Column(String(20))
    nivel_acesso = Column(String(50), default="end_user")
    avatar_url = Column(Text)
    ativo = Column(Boolean, default=True)
    ultimo_acesso = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Veiculo(Base):
    __tablename__ = "veiculos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=False)
    placa = Column(String(10), nullable=False)
    marca = Column(String(100))
    modelo = Column(String(100))
    ano = Column(Integer)
    cor = Column(String(50))
    tipo = Column(String(50))
    status = Column(String(50), default="ativo")
    quilometragem_atual = Column(Integer, default=0)
    data_ultima_manutencao = Column(DateTime(timezone=True))
    data_proxima_manutencao = Column(DateTime(timezone=True))
    custo_mensal_estimado = Column(Numeric(10, 2))
    documentos = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TicketSuporte(Base):
    __tablename__ = "tickets_suporte"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"))
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    tipo = Column(String(50), nullable=False)
    categoria = Column(String(100))
    prioridade = Column(String(20), default="media")
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    status = Column(String(50), default="aberto")
    resposta_staff = Column(Text)
    resolvido_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"))
    data_resolucao = Column(DateTime(timezone=True))
    satisfacao = Column(Integer)
    anexos = Column(JSONB, default=list)
    metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
