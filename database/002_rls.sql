-- ============================================
-- ROW LEVEL SECURITY - ISOLAMENTO TOTAL
-- ============================================

ALTER TABLE planos ENABLE ROW LEVEL SECURITY;
ALTER TABLE empresas ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE veiculos ENABLE ROW LEVEL SECURITY;
ALTER TABLE imoveis ENABLE ROW LEVEL SECURITY;
ALTER TABLE manutencoes_veiculos ENABLE ROW LEVEL SECURITY;
ALTER TABLE rotas ENABLE ROW LEVEL SECURITY;
ALTER TABLE cobrancas_inquilinos ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs_auditoria ENABLE ROW LEVEL SECURITY;

-- PLANOS
CREATE POLICY planos_select_all ON planos FOR SELECT USING (true);
CREATE POLICY planos_manage_superadmin ON planos FOR ALL USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);

-- EMPRESAS
CREATE POLICY empresas_select_own ON empresas FOR SELECT USING (
    id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);
CREATE POLICY empresas_update_own ON empresas FOR UPDATE USING (
    id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('tenant_admin', 'manager'))
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);
CREATE POLICY empresas_insert_superadmin ON empresas FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);

-- USUARIOS
CREATE POLICY usuarios_select_tenant ON usuarios FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);
CREATE POLICY usuarios_update_own ON usuarios FOR UPDATE USING (
    id = auth.uid()
    OR EXISTS (
        SELECT 1 FROM usuarios u1 
        JOIN usuarios u2 ON u1.empresa_id = u2.empresa_id 
        WHERE u1.id = auth.uid() AND u2.id = usuarios.id 
        AND u1.nivel_acesso IN ('tenant_admin', 'manager')
    )
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);

-- VEICULOS
CREATE POLICY veiculos_select_tenant ON veiculos FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY veiculos_insert_tenant ON veiculos FOR INSERT WITH CHECK (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('tenant_admin', 'manager'))
);
CREATE POLICY veiculos_update_tenant ON veiculos FOR UPDATE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('tenant_admin', 'manager'))
);
CREATE POLICY veiculos_delete_tenant ON veiculos FOR DELETE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'tenant_admin')
);

-- IMOVEIS
CREATE POLICY imoveis_select_tenant ON imoveis FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY imoveis_insert_tenant ON imoveis FOR INSERT WITH CHECK (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('tenant_admin', 'manager'))
);
CREATE POLICY imoveis_update_tenant ON imoveis FOR UPDATE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('tenant_admin', 'manager'))
);

-- MANUTENCOES
CREATE POLICY manutencoes_select_tenant ON manutencoes_veiculos FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY manutencoes_insert_tenant ON manutencoes_veiculos FOR INSERT WITH CHECK (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('tenant_admin', 'manager'))
);

-- ROTAS
CREATE POLICY rotas_select_own ON rotas FOR SELECT USING (
    motorista_id = auth.uid()
    OR empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('tenant_admin', 'manager'))
);
CREATE POLICY rotas_insert_own ON rotas FOR INSERT WITH CHECK (motorista_id = auth.uid());

-- COBRANCAS
CREATE POLICY cobrancas_select_inquilino ON cobrancas_inquilinos FOR SELECT USING (
    inquilino_id = auth.uid()
    OR empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('tenant_admin', 'manager'))
);

-- LOGS
CREATE POLICY logs_select_admin ON logs_auditoria FOR SELECT USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin'))
);
