-- ============================================
-- MÓDULO: SUPORTE, FEEDBACK E BUGS
-- ============================================

CREATE TABLE tickets_suporte (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID REFERENCES empresas(id) ON DELETE SET NULL,
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    tipo VARCHAR(50) NOT NULL,
    categoria VARCHAR(100),
    prioridade VARCHAR(20) DEFAULT 'media',
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'aberto',
    resposta_staff TEXT,
    resolvido_por UUID REFERENCES usuarios(id),
    data_resolucao TIMESTAMPTZ,
    satisfacao INTEGER CHECK (satisfacao BETWEEN 1 AND 5),
    anexos JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE comentarios_ticket (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES tickets_suporte(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES usuarios(id),
    is_staff BOOLEAN DEFAULT false,
    conteudo TEXT NOT NULL,
    anexos JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE changelog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    versao VARCHAR(20) NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50),
    status VARCHAR(50) DEFAULT 'planejado',
    data_publicacao TIMESTAMPTZ,
    tickets_relacionados UUID[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE votos_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feedback_id UUID NOT NULL REFERENCES tickets_suporte(id) ON DELETE CASCADE,
    usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    voto INTEGER NOT NULL CHECK (voto IN (-1, 1)),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(feedback_id, usuario_id)
);

-- Índices
CREATE INDEX idx_tickets_empresa ON tickets_suporte(empresa_id);
CREATE INDEX idx_tickets_status ON tickets_suporte(status);
CREATE INDEX idx_tickets_tipo ON tickets_suporte(tipo);
CREATE INDEX idx_tickets_prioridade ON tickets_suporte(prioridade);
CREATE INDEX idx_comentarios_ticket ON comentarios_ticket(ticket_id);
CREATE INDEX idx_changelog_status ON changelog(status);

-- RLS
ALTER TABLE tickets_suporte ENABLE ROW LEVEL SECURITY;
ALTER TABLE comentarios_ticket ENABLE ROW LEVEL SECURITY;
ALTER TABLE changelog ENABLE ROW LEVEL SECURITY;
ALTER TABLE votos_feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY tickets_select_own ON tickets_suporte FOR SELECT USING (
    usuario_id = auth.uid()
    OR empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);
CREATE POLICY tickets_insert_own ON tickets_suporte FOR INSERT WITH CHECK (usuario_id = auth.uid());
CREATE POLICY tickets_update_staff ON tickets_suporte FOR UPDATE USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);

CREATE POLICY comentarios_select ON comentarios_ticket FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM tickets_suporte t 
        WHERE t.id = ticket_id 
        AND (t.usuario_id = auth.uid() OR t.empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid()))
    )
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);
CREATE POLICY comentarios_insert ON comentarios_ticket FOR INSERT WITH CHECK (
    usuario_id = auth.uid()
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);

CREATE POLICY changelog_select_all ON changelog FOR SELECT USING (true);
CREATE POLICY changelog_manage_superadmin ON changelog FOR ALL USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);

CREATE POLICY votos_select_all ON votos_feedback FOR SELECT USING (true);
CREATE POLICY votos_insert_own ON votos_feedback FOR INSERT WITH CHECK (usuario_id = auth.uid());

-- Trigger
CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON tickets_suporte
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
