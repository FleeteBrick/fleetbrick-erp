-- ============================================
-- FUNÇÕES E TRIGGERS
-- ============================================

CREATE OR REPLACE FUNCTION count_veiculos_empresa(p_empresa_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM veiculos WHERE empresa_id = p_empresa_id AND status != 'vendido');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION count_imoveis_empresa(p_empresa_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM imoveis WHERE empresa_id = p_empresa_id AND status != 'vendido');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION check_plano_limit(p_empresa_id UUID, p_tipo VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_plano_id UUID;
    v_max INTEGER;
    v_atual INTEGER;
BEGIN
    SELECT plano_id INTO v_plano_id FROM empresas WHERE id = p_empresa_id;

    IF p_tipo = 'veiculo' THEN
        SELECT max_veiculos INTO v_max FROM planos WHERE id = v_plano_id;
        v_atual := count_veiculos_empresa(p_empresa_id);
    ELSIF p_tipo = 'imovel' THEN
        SELECT max_imoveis INTO v_max FROM planos WHERE id = v_plano_id;
        v_atual := count_imoveis_empresa(p_empresa_id);
    ELSE
        RETURN false;
    END IF;

    RETURN v_atual < v_max;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_planos_updated_at BEFORE UPDATE ON planos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_empresas_updated_at BEFORE UPDATE ON empresas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_veiculos_updated_at BEFORE UPDATE ON veiculos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_imoveis_updated_at BEFORE UPDATE ON imoveis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO logs_auditoria (
        empresa_id, usuario_id, tabela_afetada, operacao, registro_id,
        dados_anteriores, dados_novos
    ) VALUES (
        COALESCE(NEW.empresa_id, OLD.empresa_id),
        auth.uid(),
        TG_TABLE_NAME,
        TG_OP,
        COALESCE(NEW.id, OLD.id),
        CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER audit_veiculos AFTER INSERT OR UPDATE OR DELETE ON veiculos
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
CREATE TRIGGER audit_imoveis AFTER INSERT OR UPDATE OR DELETE ON imoveis
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
CREATE TRIGGER audit_cobrancas AFTER INSERT OR UPDATE OR DELETE ON cobrancas_inquilinos
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
