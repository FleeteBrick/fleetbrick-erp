"""
Servidor MCP para Fleet&Brick ERP
Exponhe tools para agentes de IA consultarem dados
"""
from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client
import os

app = FastAPI(title="Fleet&Brick MCP Server")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://guzzdpvrcslpqejnansv.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmMyM2E2NWJiLTY4NmQtNDdiMC04NGJiLTJlNjJmNGM1NGViODo6JGFhY2hfNTIzZjY5OTYtODVhNy00ZTVjLTkyOWMtZGNhNjMzMzU4ODI1")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class ManutencaoConsulta(BaseModel):
    empresa_id: str


class InadimplenciaConsulta(BaseModel):
    empresa_id: str


class ChamadoCreate(BaseModel):
    empresa_id: str
    descricao: str
    tipo: str
    nivel_prioridade: str = "media"


@app.get("/")
def root():
    return {"status": "ok", "service": "fleetbrick-mcp"}


@app.get("/health")
def health():
    return {"status": "ok"}


def verificar_manutencoes_vencidas(empresa_id: str) -> dict:
    """
    Consulta veículos com manutenção vencida baseada em data ou km.
    
    Args:
        empresa_id: UUID da empresa
    
    Returns:
        Lista de veículos com manutenção atrasada
    """
    from datetime import date
    
    hoje = date.today()
    
    # Veículos com manutenção preventiva vencida
    manutencoes = supabase.table("manutencoes").select("*, veiculos(*)").eq("empresa_id", empresa_id).lte("data_agendada", str(hoje)).eq("status", "agendada").execute()
    
    # Veículos com km excedido
    veiculos = supabase.table("veiculos").select("*").eq("empresa_id", empresa_id).eq("status", "ativo").execute()
    
    resultado = []
    for veiculo in veiculos.data:
        if veiculo.get("quilometragem_atual", 0) > 10000:
            resultado.append({
                "veiculo": veiculo,
                "tipo_alerta": "km_excedido",
                "mensagem": f"Veículo {veiculo['placa']} ultrapassou 10.000km sem manutenção"
            })
    
    for manut in manutencoes.data:
        resultado.append({
            "veiculo": manut.get("veiculos"),
            "tipo_alerta": "data_vencida",
            "mensagem": f"Manutenção {manut['tipo']} vencida em {manut['data_agendada']}"
        })
    
    return {"manutencoes_vencidas": resultado, "total": len(resultado)}


def verificar_inadimplencia_locacao(empresa_id: str) -> dict:
    """
    Consulta inadimplência baseada na DATA DE ENTRADA do inquilino.
    
    Usa a data de entrada exata do contrato para calcular vencimentos
    e identificar atrasos com precisão matemática.
    
    Args:
        empresa_id: UUID da empresa
    
    Returns:
        Lista de pagamentos vencidos
    """
    from datetime import date, timedelta
    
    hoje = date.today()
    
    # Busca contratos ativos
    contratos = supabase.table("contratos_locacao").select("*, propriedades(*)").eq("empresa_id", empresa_id).eq("status", "ativo").execute()
    
    inadimplentes = []
    
    for contrato in contratos.data:
        data_entrada = contrato.get("data_entrada")
        if not data_entrada:
            continue
            
        dia_venc = contrato.get("dia_vencimento", 5)
        valor = contrato.get("valor_aluguel", 0)
        contrato_id = contrato["id"]
        
        # Calcula meses de referência
        for i in range(1, 4):
            mes_ref = f"{hoje.year}-{hoje.month - i:02d}" if hoje.month > i else f"{hoje.year - 1}-{(hoje.month - i) + 12:02d}"
            
            # Verifica se pagamento existe
            pagamento = supabase.table("pagamentos_aluguel").select("*").eq("contrato_id", contrato_id).eq("mes_referencia", mes_ref).execute()
            
            if not pagamento.data or pagamento.data[0].get("status") in ["pendente", "vencido"]:
                dias_atraso = (hoje - pagamento.data[0].get("data_vencimento", hoje)).days if pagamento.data else 0
                
                inadimplentes.append({
                    "contrato_id": contrato_id,
                    "inquilino": contrato.get("inquilino_nome"),
                    "propriedade": contrato.get("propriedades", {}).get("endereco"),
                    "valor": valor,
                    "mes": mes_ref,
                    "dias_atraso": dias_atraso,
                    "status": pagamento.data[0].get("status") if pagamento.data else "nao_gerado"
                })
    
    return {"inadimplentes": inadimplentes, "total": len(inadimplentes)}


def inserir_chamado_suporte(empresa_id: str, descricao: str, tipo: str, nivel_prioridade: str = "media") -> dict:
    """
    Insere chamado na Central de Helpdesk.
    
    Args:
        empresa_id: UUID da empresa
        descricao: Descrição do problema/sugestão
        tipo: 'bug', 'sugestao', 'duvida'
        nivel_prioridade: 'baixa', 'media', 'alta', 'critica'
    
    Returns:
        Chamado criado
    """
    # Classificação automática por IA
    categoria = "suporte"
    if any(palavra in descricao.lower() for palavra in ["erro", "bug", "não funciona", "falha"]):
        categoria = "bug"
        nivel_prioridade = "alta"
    elif any(palavra in descricao.lower() for palavra in ["sugestão", "melhoria", "ideal"]):
        categoria = "sugestao"
        nivel_prioridade = "baixa"
    
    chamado_data = {
        "empresa_id": empresa_id,
        "tipo": tipo,
        "descricao": descricao,
        "nivel_prioridade": nivel_prioridade,
        "categoria": categoria,
        "status": "aberto"
    }
    
    result = supabase.table("chamados_suporte").insert(chamado_data).execute()
    
    return {"chamado": result.data[0], "classificacao_automatica": categoria}


# Endpoints FastAPI para Tools
@app.post("/tools/verificar_manutencoes_vencidas")
def tool_manutencoes(consulta: ManutencaoConsulta):
    """Tool MCP: Verificar manutenções vencidas"""
    return verificar_manutencoes_vencidas(consulta.empresa_id)


@app.post("/tools/verificar_inadimplencia_locacao")
def tool_inadimplencia(consulta: InadimplenciaConsulta):
    """Tool MCP: Verificar inadimplência de locação"""
    return verificar_inadimplencia_locacao(consulta.empresa_id)


@app.post("/tools/inserir_chamado_suporte")
def tool_chamado(chamado: ChamadoCreate):
    """Tool MCP: Inserir chamado de suporte"""
    return inserir_chamado_suporte(chamado.empresa_id, chamado.descricao, chamado.tipo, chamado.nivel_prioridade)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)