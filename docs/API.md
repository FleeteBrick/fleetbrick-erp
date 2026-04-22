# 📚 Fleet&Brick API Documentation

## Base URL
```
Development: http://localhost:8000
Production: https://api.fleetbrick.com
```

## Autenticação
Todas as rotas (exceto auth) requerem Bearer token no header:
```
Authorization: Bearer <jwt_token>
```

## Endpoints

### Auth
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /api/auth/login | Login de usuário |
| POST | /api/auth/register | Registro de novo tenant |
| POST | /api/auth/logout | Logout |

### Planos (Super Admin)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /api/planos | Listar planos |
| POST | /api/planos | Criar plano |
| PUT | /api/planos/{id} | Atualizar plano |
| DELETE | /api/planos/{id} | Desativar plano |

### Veículos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /api/veiculos/novo | Criar veículo (com validação de limite) |
| GET | /api/veiculos | Listar veículos |
| GET | /api/veiculos/{id} | Obter veículo |
| PUT | /api/veiculos/{id} | Atualizar veículo |
| DELETE | /api/veiculos/{id} | Remover veículo |

### Tickets (Suporte)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /api/tickets | Criar ticket |
| GET | /api/tickets | Listar todos (Super Admin) |
| GET | /api/tickets/meus | Meus tickets |
| PUT | /api/tickets/{id} | Atualizar ticket |
| GET | /api/tickets/estatisticas | Estatísticas |

## Códigos de Erro
| Código | Significado |
|--------|-------------|
| 402 | Pagamento necessário (assinatura inativa) |
| 403 | Limite do plano atingido |
| 404 | Recurso não encontrado |
| 409 | Conflito (placa duplicada, etc) |
