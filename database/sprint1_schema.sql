-- =====================================================
-- FLEET&BRICK ERP - BANCO DE DADOS COMPLETO
-- Sprint 1: O Coração do Banco de Dados
-- =====================================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- TABELAS GLOBAIS (Super Admin)
-- =====================================================

-- Planos de Assinatura
CREATE TABLE planos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2) NOT NULL DEFAULT 197.00,
    max_veiculos INTEGER NOT NULL DEFAULT 5,
    max_imoveis INTEGER NOT NULL DEFAULT 10,
    max_usuarios INTEGER NOT NULL DEFAULT 3,
    recursos JSONB DEFAULT '[]'::jsonb,
    Popular BOOLEAN DEFAULT false,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Empresas (Tenants)
CREATE TABLE empresas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) UNIQUE,
    email VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    plano_id UUID NOT NULL REFERENCES planos(id),
    asaas_customer_id VARCHAR(100),
    asaas_subscription_id VARCHAR(100),
    asaas_subconta_id VARCHAR(100),
    status_assinatura VARCHAR(50) DEFAULT 'trial',
    data_vencimento TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '14 days'),
    configuracoes JSONB DEFAULT '{}'::jsonb,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usuários (Autenticação)
CREATE TABLE usuarios (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    nivel_acesso VARCHAR(50) NOT NULL DEFAULT 'end_user',
    avatar_url TEXT,
    ativo BOOLEAN DEFAULT true,
    ultimo_acesso TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- =====================================================
-- MÓDULO IMÓVEIS (Brick)
-- =====================================================

-- Propriedades
CREATE TABLE propriedades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    codigo_interno VARCHAR(50),
    endereco TEXT NOT NULL,
    cep VARCHAR(10),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    tipo VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'livre',
    valor_aluguel DECIMAL(10,2),
    valor_condominio DECIMAL(10,2),
    area_m2 DECIMAL(10,2),
    quartos INTEGER,
    banheiros INTEGER,
    vagas_garagem INTEGER,
    descricao TEXT,
    caracteristicas JSONB DEFAULT '[]'::jsonb,
    imagens JSONB DEFAULT '[]'::jsonb,
    data_vistoria DATE,
    vistoria_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contratos de Locação
CREATE TABLE contratos_locacao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    propriedade_id UUID NOT NULL REFERENCES propriedades(id) ON DELETE CASCADE,
    inquilino_id UUID REFERENCES usuarios(id),
    inquilino_nome VARCHAR(255) NOT NULL,
    inquilino_cpf VARCHAR(14),
    inquilino_email VARCHAR(255),
    inquilino_telefone VARCHAR(20),
    data_entrada DATE NOT NULL,
    data_inicio_contrato DATE NOT NULL,
    data_fim_contrato DATE,
    valor_aluguel DECIMAL(10,2) NOT NULL,
    dia_vencimento INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'ativo',
    garantias JSONB DEFAULT '[]'::jsonb,
    obs TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pagamentos de Aluguel
CREATE TABLE pagamentos_aluguel (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    contrato_id UUID NOT NULL REFERENCES contratos_locacao(id) ON DELETE CASCADE,
    asaas_payment_id VARCHAR(100),
    asaas_billingype VARCHAR(50),
    valor DECIMAL(10,2) NOT NULL,
    valor_pago DECIMAL(10,2),
    data_vencimento DATE NOT NULL,
    data_pagamento DATE,
    status VARCHAR(50) DEFAULT 'pendente',
    mes_referencia VARCHAR(7) NOT NULL,
    link_boleto TEXT,
    pix_copia_cola TEXT,
    pix_qrcode TEXT,
    notificado BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- MÓDULO FROTAS (Fleet)
-- =====================================================

-- Veículos
CREATE TABLE veiculos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    placa VARCHAR(10) NOT NULL,
    chassi VARCHAR(17),
    marca VARCHAR(100),
    modelo VARCHAR(100),
    ano INTEGER,
    cor VARCHAR(50),
    tipo_combustivel VARCHAR(50),
    quilometragem_atual INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'ativo',
    data_ultima_manutencao DATE,
    valor_fip DECIMAL(10,2),
    documentos JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, placa)
);

-- Manutenções
CREATE TABLE manutencoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    veiculo_id UUID NOT NULL REFERENCES veiculos(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL,
    descricao TEXT NOT NULL,
    data_agendada DATE NOT NULL,
    data_realizada DATE,
    custo DECIMAL(10,2),
    km_odometro INTEGER,
    status VARCHAR(50) DEFAULT 'agendada',
    responsavel_id UUID REFERENCES usuarios(id),
    anexos JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Rotas
CREATE TABLE rotas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    veiculo_id UUID NOT NULL REFERENCES veiculos(id) ON DELETE CASCADE,
    motorista_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    origem TEXT NOT NULL,
    destino TEXT NOT NULL,
    distancia_km DECIMAL(10,2),
    data_inicio TIMESTAMPTZ DEFAULT NOW(),
    data_fim TIMESTAMPTZ,
    status VARCHAR(50) DEFAULT 'em_andamento',
    obs TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Checklists de Vistoria
CREATE TABLE checklists_vistoria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    veiculo_id UUID NOT NULL REFERENCES veiculos(id) ON DELETE CASCADE,
    motoristal_id UUID NOT NULL REFERENCES usuarios(id),
    tipo VARCHAR(50) NOT NULL,
    km_inicial INTEGER,
    km_final INTEGER,
    data_check TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'pendente',
    itens JSONB NOT NULL,
    anexos JSONB DEFAULT '[]'::jsonb,
    obs TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Abastecimentos
CREATE TABLE abastecimentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    veiculo_id UUID NOT NULL REFERENCES veiculos(id) ON DELETE CASCADE,
    motoristal_id UUID NOT NULL REFERENCES usuarios(id),
    data_abastecimento DATE NOT NULL,
    litros DECIMAL(10,3) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    km_odometro INTEGER,
    combustivel VARCHAR(50),
    posto TEXT,
    nota_fiscal_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- MÓDULO SUPORTE
-- =====================================================

-- Chamados de Suporte
CREATE TABLE chamados_suporte (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID REFERENCES empresas(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES usuarios(id),
    tipo VARCHAR(50) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    nivel_prioridade VARCHAR(50) DEFAULT 'media',
    status VARCHAR(50) DEFAULT 'aberto',
    categoria VARCHAR(50),
    resposta TEXT,
    resolvido_por UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- ÍNDICES DE PERFORMANCE
-- =====================================================
CREATE INDEX idx_empresas_plano ON empresas(plano_id);
CREATE INDEX idx_propriedades_empresa ON propriedades(empresa_id);
CREATE INDEX idx_contratos_propriedade ON contratos_locacao(propriedade_id);
CREATE INDEX idx_contratos_inquilino ON contratos_locacao(inquilino_id);
CREATE INDEX idx_pagamentos_contrato ON pagamentos_aluguel(contrato_id);
CREATE INDEX idx_pagamentos_status ON pagamentos_aluguel(status);
CREATE INDEX idx_veiculos_empresa ON veiculos(empresa_id);
CREATE INDEX idx_manutencoes_veiculo ON manutencoes(veiculo_id);
CREATE INDEX idx_rotas_veiculo ON rotas(veiculo_id);
CREATE INDEX idx_rotas_motorista ON rotas(motorista_id);
CREATE INDEX idx_checklists_veiculo ON checklists_vistoria(veiculo_id);
CREATE INDEX idx_abastecimentos_veiculo ON abastecimentos(veiculo_id);
CREATE INDEX idx_chamados_empresa ON chamados_suporte(empresa_id);
CREATE INDEX idx_chamados_status ON chamados_suporte(status);
CREATE INDEX idx_usuarios_empresa ON usuarios(empresa_id);