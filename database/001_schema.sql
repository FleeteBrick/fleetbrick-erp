-- ============================================
-- FLEET&BRICK ERP - SCHEMA COMPLETO
-- ============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- TABELA: PLANOS (Gerenciada pelo Super Admin)
-- ============================================
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
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELA: EMPRESAS (Tenants)
-- ============================================
CREATE TABLE empresas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18) UNIQUE,
    email VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    plano_id UUID NOT NULL REFERENCES planos(id),
    asaas_customer_id VARCHAR(100),
    asaas_subscription_id VARCHAR(100),
    status_assinatura VARCHAR(50) DEFAULT 'trial',
    data_vencimento_trial TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '14 days'),
    configuracoes JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELA: USUARIOS (Autenticação via Supabase Auth)
-- ============================================
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
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELA: VEICULOS
-- ============================================
CREATE TABLE veiculos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    placa VARCHAR(10) NOT NULL,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    ano INTEGER,
    cor VARCHAR(50),
    tipo VARCHAR(50),
    status VARCHAR(50) DEFAULT 'ativo',
    quilometragem_atual INTEGER DEFAULT 0,
    data_ultima_manutencao DATE,
    data_proxima_manutencao DATE,
    custo_mensal_estimado DECIMAL(10,2),
    documentos JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(empresa_id, placa)
);

-- ============================================
-- TABELA: IMOVEIS
-- ============================================
CREATE TABLE imoveis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    codigo_interno VARCHAR(50),
    endereco TEXT NOT NULL,
    cep VARCHAR(10),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    tipo VARCHAR(50),
    status VARCHAR(50) DEFAULT 'disponivel',
    valor_aluguel DECIMAL(10,2),
    valor_condominio DECIMAL(10,2),
    area_m2 DECIMAL(10,2),
    quartos INTEGER,
    banheiros INTEGER,
    vagas_garagem INTEGER,
    inquilino_atual UUID REFERENCES usuarios(id),
    data_proxima_vistoria DATE,
    documentos JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELA: MANUTENCOES_VEICULOS
-- ============================================
CREATE TABLE manutencoes_veiculos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    veiculo_id UUID NOT NULL REFERENCES veiculos(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL,
    descricao TEXT NOT NULL,
    data_agendada DATE NOT NULL,
    data_realizada DATE,
    custo DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'agendada',
    responsavel_id UUID REFERENCES usuarios(id),
    notificado BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELA: ROTAS (End-User: Motorista)
-- ============================================
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
    observacoes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELA: COBRANCAS_INQUILINOS (White-label Asaas)
-- ============================================
CREATE TABLE cobrancas_inquilinos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    imovel_id UUID NOT NULL REFERENCES imoveis(id) ON DELETE CASCADE,
    inquilino_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    asaas_payment_id VARCHAR(100),
    valor DECIMAL(10,2) NOT NULL,
    vencimento DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pendente',
    mes_referencia VARCHAR(7) NOT NULL,
    boleto_url TEXT,
    pix_qr_code TEXT,
    pix_payload TEXT,
    notificado BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELA: LOGS_AUDITORIA
-- ============================================
CREATE TABLE logs_auditoria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID REFERENCES empresas(id),
    usuario_id UUID REFERENCES usuarios(id),
    tabela_afetada VARCHAR(100) NOT NULL,
    operacao VARCHAR(20) NOT NULL,
    registro_id UUID,
    dados_anteriores JSONB,
    dados_novos JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ÍNDICES DE PERFORMANCE
-- ============================================
CREATE INDEX idx_veiculos_empresa ON veiculos(empresa_id);
CREATE INDEX idx_imoveis_empresa ON imoveis(empresa_id);
CREATE INDEX idx_usuarios_empresa ON usuarios(empresa_id);
CREATE INDEX idx_manutencoes_veiculo ON manutencoes_veiculos(veiculo_id);
CREATE INDEX idx_rotas_motorista ON rotas(motorista_id);
CREATE INDEX idx_cobrancas_inquilino ON cobrancas_inquilinos(inquilino_id);
CREATE INDEX idx_logs_auditoria_empresa ON logs_auditoria(empresa_id, created_at);
