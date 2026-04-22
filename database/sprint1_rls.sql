-- =====================================================
-- POLÍTICAS RLS (Row Level Security)
-- =====================================================

-- =====================================================
-- GLOBAIS (Super Admin)
-- =====================================================

ALTER TABLE planos ENABLE ROW LEVEL SECURITY;
ALTER TABLE empresas ENABLE ROW LEVEL SECURITY;
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- Planos: Todos podem ler, apenas super_admin gerencia
CREATE POLICY planos_select ON planos FOR SELECT USING (true);
CREATE POLICY planos_insert ON planos FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);
CREATE POLICY planos_update ON planos FOR UPDATE USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);
CREATE POLICY planos_delete ON planos FOR DELETE USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);

-- Empresas: Leitura via usuário logado
CREATE POLICY empresas_select ON empresas FOR SELECT USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND empresa_id = empresas.id)
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);
CREATE POLICY empresas_update ON empresas FOR UPDATE USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin'))
);

-- Usuários: Isolamento por empresa
CREATE POLICY usuarios_select ON usuarios FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
    OR nivel_acesso = 'super_admin'
);
CREATE POLICY usuarios_update ON usuarios FOR UPDATE USING (
    id = auth.uid()
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin'))
);

-- =====================================================
-- IMÓVEIS (Brick)
-- =====================================================

ALTER TABLE propriedades ENABLE ROW LEVEL SECURITY;
ALTER TABLE contratos_locacao ENABLE ROW LEVEL SECURITY;
ALTER TABLE pagamentos_aluguel ENABLE ROW LEVEL SECURITY;

-- Propriedades: Isolamento por empresa
CREATE POLICY propriedades_select ON propriedades FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY propriedades_insert ON propriedades FOR INSERT WITH CHECK (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin', 'manager'))
);
CREATE POLICY propriedades_update ON propriedades FOR UPDATE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin', 'manager'))
);
CREATE POLICY propriedades_delete ON propriedades FOR DELETE USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'tenant_admin')
);

-- Contratos: Isolamento por empresa
CREATE POLICY contratos_select ON contratos_locacao FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY contratos_insert ON contratos_locacao FOR INSERT WITH CHECK (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin', 'manager'))
);
CREATE POLICY contratos_update ON contratos_locacao FOR UPDATE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin', 'manager'))
);

-- Pagamentos: Isolamento por empresa
CREATE POLICY pagamentos_select ON pagamentos_aluguel FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY pagamentos_update ON pagamentos_aluguel FOR UPDATE USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);

-- =====================================================
-- FROTAS (Fleet)
-- =====================================================

ALTER TABLE veiculos ENABLE ROW LEVEL SECURITY;
ALTER TABLE manutencoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE rotas ENABLE ROW LEVEL SECURITY;
ALTER TABLE checklists_vistoria ENABLE ROW LEVEL SECURITY;
ALTER TABLE abastecimentos ENABLE ROW LEVEL SECURITY;

-- Veículos: Isolamento por empresa
CREATE POLICY veiculos_select ON veiculos FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY veiculos_insert ON veiculos FOR INSERT WITH CHECK (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin', 'manager'))
);
CREATE POLICY veiculos_update ON veiculos FOR UPDATE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin', 'manager'))
);
CREATE POLICY veiculos_delete ON veiculos FOR DELETE USING (
    EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'tenant_admin')
);

-- Manutenções
CREATE POLICY manutencoes_select ON manutencoes FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY manutencoes_insert ON manutencoes FOR INSERT WITH CHECK (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin', 'manager'))
);
CREATE POLICY manutencoes_update ON manutencoes FOR UPDATE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin', 'manager'))
);

-- Rotas
CREATE POLICY rotas_select ON rotas FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
    OR motoristal_id = auth.uid()
);
CREATE POLICY rotas_insert ON rotas FOR INSERT WITH CHECK (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid()) AND motoristal_id = auth.uid()
);
CREATE POLICY rotas_update ON rotas FOR UPDATE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
    OR motoristal_id = auth.uid()
);

-- Checklists
CREATE POLICY checklists_select ON checklists_vistoria FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
    OR motoristal_id = auth.uid()
);
CREATE POLICY checklists_insert ON checklists_vistoria FOR INSERT WITH CHECK (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY checklists_update ON checklists_vistoria FOR UPDATE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);

-- Abastecimentos
CREATE POLICY abastecimentos_select ON abastecimentos FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY abastecimentos_insert ON abastecimentos FOR INSERT WITH CHECK (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
);
CREATE POLICY abastecimentos_update ON abastecimentos FOR UPDATE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin', 'manager'))
);

-- =====================================================
-- SUPORTE
-- =====================================================

ALTER TABLE chamados_suporte ENABLE ROW LEVEL SECURITY;

-- Chamados: Todos podem ver os próprios, super_admin vê todos
CREATE POLICY chamados_select ON chamados_suporte FOR SELECT USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid())
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);
CREATE POLICY chamados_insert ON chamados_suporte FOR INSERT WITH CHECK (true);
CREATE POLICY chamados_update ON chamados_suporte FOR UPDATE USING (
    empresa_id IN (SELECT empresa_id FROM usuarios WHERE id = auth.uid() AND nivel_acesso IN ('super_admin', 'tenant_admin', 'manager'))
    OR EXISTS (SELECT 1 FROM usuarios WHERE id = auth.uid() AND nivel_acesso = 'super_admin')
);