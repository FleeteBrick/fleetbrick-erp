-- =====================================================
-- FLEET&BRICK ERP - SCHEMA DEFINITIVO
-- Execute no Supabase SQL Editor
-- =====================================================

-- 1. Extensões
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Criar tabelas (sem DROP para evitar erros)

-- Planos
CREATE TABLE IF NOT EXISTS planos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    preco DECIMAL(10,2) NOT NULL DEFAULT 197.00,
    max_veiculos INTEGER NOT NULL DEFAULT 5,
    max_imoveis INTEGER NOT NULL DEFAULT 10,
    max_usuarios INTEGER NOT NULL DEFAULT 3,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Empresas
CREATE TABLE IF NOT EXISTS empresas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18),
    email VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    plano_id UUID REFERENCES planos(id),
    status_assinatura VARCHAR(50) DEFAULT 'trial',
    data_vencimento TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '14 days'),
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Propriedades
CREATE TABLE IF NOT EXISTS propriedades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    endereco TEXT NOT NULL,
    cep VARCHAR(10),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    tipo VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'livre',
    valor_aluguel DECIMAL(10,2),
    area_m2 DECIMAL(10,2),
    quartos INTEGER,
    banheiros INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contratos
CREATE TABLE IF NOT EXISTS contratos_locacao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    propriedade_id UUID REFERENCES propriedades(id),
    inquilino_nome VARCHAR(255) NOT NULL,
    inquilino_email VARCHAR(255),
    inquilino_telefone VARCHAR(20),
    data_entrada DATE NOT NULL,
    valor_aluguel DECIMAL(10,2) NOT NULL,
    dia_vencimento INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'ativo',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pagamentos
CREATE TABLE IF NOT EXISTS pagamentos_aluguel (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    contrato_id UUID REFERENCES contratos_locacao(id),
    valor DECIMAL(10,2) NOT NULL,
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    status VARCHAR(50) DEFAULT 'pendente',
    mes_referencia VARCHAR(7) NOT NULL,
    link_boleto TEXT,
    pix_copia_cola TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Veículos
CREATE TABLE IF NOT EXISTS veiculos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    placa VARCHAR(10) NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    ano INTEGER,
    cor VARCHAR(50),
    tipo_combustivel VARCHAR(50) DEFAULT 'flex',
    quilometragem_atual INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'ativo',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Manutenções
CREATE TABLE IF NOT EXISTS manutencoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    veiculo_id UUID REFERENCES veiculos(id),
    tipo VARCHAR(50) NOT NULL,
    descricao TEXT NOT NULL,
    data_agendada DATE NOT NULL,
    data_realizada DATE,
    custo DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'agendada',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chamados
CREATE TABLE IF NOT EXISTS chamados_suporte (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID REFERENCES empresas(id),
    usuario_id UUID,
    tipo VARCHAR(50) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    nivel_prioridade VARCHAR(50) DEFAULT 'media',
    status VARCHAR(50) DEFAULT 'aberto',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Seed - Dados Iniciais
INSERT INTO planos (nome, slug, preco, max_veiculos, max_imoveis, max_usuarios) VALUES
('Starter', 'starter', 197.00, 5, 10, 3),
('Pro', 'pro', 497.00, 20, 50, 10),
('Enterprise', 'enterprise', 997.00, 999, 999, 999)
ON CONFLICT (slug) DO NOTHING;