-- =====================================================
-- SEED DATA - DADOS INICIAIS
-- =====================================================

-- Planos
INSERT INTO planos (nome, slug, descricao, preco, max_veiculos, max_imoveis, max_usuarios, Popular) VALUES
('Starter', 'starter', 'Plano básico para pequenas empresas', 197.00, 5, 10, 3, true),
('Pro', 'pro', 'Plano profissional com mais recursos', 497.00, 20, 50, 10, false),
('Enterprise', 'enterprise', 'Plano enterprise ilimitado', 997.00, 999, 999, 999, false);

-- Criar função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at automático
CREATE TRIGGER update_planos_updated_at BEFORE UPDATE ON planos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_empresas_updated_at BEFORE UPDATE ON empresas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_propriedades_updated_at BEFORE UPDATE ON propriedades
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contratos_updated_at BEFORE UPDATE ON contratos_locacao
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pagamentos_updated_at BEFORE UPDATE ON pagamentos_aluguel
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_veiculos_updated_at BEFORE UPDATE ON veiculos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chamados_updated_at BEFORE UPDATE ON chamados_suporte
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();