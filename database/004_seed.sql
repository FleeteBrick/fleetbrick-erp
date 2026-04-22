-- ============================================
-- SEED INICIAL
-- ============================================

INSERT INTO planos (nome, slug, descricao, preco, max_veiculos, max_imoveis, max_usuarios, recursos)
VALUES 
    ('Starter', 'starter', 'Ideal para pequenas frotas e imobiliárias', 197.00, 5, 10, 3, '["suporte_email", "relatorios_basicos"]'),
    ('Pro', 'pro', 'Para empresas em crescimento', 497.00, 20, 50, 10, '["suporte_email", "relatorios_avancados", "ia_suporte", "white_label"]'),
    ('Enterprise', 'enterprise', 'Solução completa e customizável', 997.00, 999, 999, 999, '["todos_recursos", "api_dedicada", "suporte_prioritario"]');

-- Criar super admin inicial (executar após criar usuário no Auth)
-- INSERT INTO usuarios (id, empresa_id, nome, email, nivel_acesso) 
-- VALUES ('uuid-do-super-admin', NULL, 'Admin Fleet&Brick', 'fleetebrick@gmail.com', 'super_admin');
