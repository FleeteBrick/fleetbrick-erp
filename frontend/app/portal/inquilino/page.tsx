"use client"

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useAuth } from '@/hooks/useAuth'

interface Contrato {
  id: string
  propriedade_id: string
  inquilino_nome: string
  data_entrada: string
  valor_aluguel: number
  dia_vencimento: number
  status: string
  propriedades?: { endereco: string }
}

interface Pagamento {
  id: string
  mes_referencia: string
  valor: number
  data_vencimento: string
  status: string
  link_boleto: string
  pix_copia_cola: string
}

export default function InquilinoPage() {
  const [contrato, setContrato] = useState<Contrato | null>(null)
  const [pagamentos, setPagamentos] = useState<Pagamento[]>([])
  const [loading, setLoading] = useState(true)
  const supabase = createClient()
  const { user } = useAuth()

  useEffect(() => {
    if (user) carregarDados()
  }, [user])

  async function carregarDados() {
    if (!user) return
    
    const { data: usuario } = await supabase
      .from('usuarios')
      .select('empresa_id')
      .eq('id', user.id)
      .single()

    if (!usuario) return

    const { data: contratoData } = await supabase
      .from('contratos_locacao')
      .select('*, propriedades(endereco)')
      .eq('inquilino_id', user.id)
      .eq('status', 'ativo')
      .single()

    if (contratoData) {
      setContrato(contratoData)
      
      const { data: pagamentosData } = await supabase
        .from('pagamentos_aluguel')
        .select('*')
        .eq('contrato_id', contratoData.id)
        .order('data_vencimento', { ascending: false })
        .limit(3)
      
      setPagamentos(pagamentosData || [])
    }
    setLoading(false)
  }

  function copiarPix() {
    if (pagamentos[0]?.pix_copia_cola) {
      navigator.clipboard.writeText(pagamentos[0].pix_copia_cola)
      alert('Pix copiado!')
    }
  }

  if (loading) return <div className="p-8 text-center">Carregando...</div>

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-md mx-auto p-4">
        <h1 className="text-2xl font-bold text-center mb-6">🏠 Portal Inquilino</h1>

        {contrato ? (
          <>
            <div className="bg-white rounded-xl shadow-sm border p-6 mb-4">
              <h2 className="text-sm text-gray-500 mb-1">Seu Imóvel</h2>
              <p className="font-medium">{contrato.propriedades?.endereco}</p>
              
              <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Valor Mensal</p>
                  <p className="font-bold">R$ {contrato.valor_aluguel?.toLocaleString('pt-BR')}</p>
                </div>
                <div>
                  <p className="text-gray-500">Vencimento</p>
                  <p className="font-bold">Dia {contrato.dia_vencimento}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6 mb-4">
              <h2 className="text-lg font-bold mb-4">Ações Rápidas</h2>
              
              {pagamentos[0] && (
                <div className="space-y-3">
                  <button
                    onClick={() => {
                      if (pagamentos[0].link_boleto) {
                        window.open(pagamentos[0].link_boleto, '_blank')
                      }
                    }}
                    disabled={!pagamentos[0].link_boleto}
                    className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium disabled:opacity-50"
                  >
                    📄 Baixar Boleto do Mês
                  </button>
                  
                  <button
                    onClick={copiarPix}
                    disabled={!pagamentos[0]?.pix_copia_cola}
                    className="w-full bg-green-600 text-white py-3 rounded-lg font-medium disabled:opacity-50"
                  >
                    📋 Copiar Código Pix
                  </button>
                </div>
              )}
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-lg font-bold mb-4">Histórico</h2>
              
              <div className="space-y-3">
                {pagamentos.map(pag => (
                  <div key={pag.id} className="flex justify-between items-center border-b pb-2">
                    <div>
                      <p className="font-medium">{pag.mes_referencia}</p>
                      <p className="text-sm text-gray-500">Venc: {pag.data_vencimento}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">R$ {pag.valor?.toLocaleString('pt-BR')}</p>
                      <p className={`text-sm ${pag.status === 'pago' ? 'text-green-600' : 'text-red-600'}`}>
                        {pag.status === 'pago' ? '✓ Pago' : '⏳ Pendente'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border p-8 text-center">
            <p className="text-gray-600">Nenhum contrato ativo encontrado.</p>
            <p className="text-sm text-gray-500 mt-2">Entre em contato com o gestor.</p>
          </div>
        )}

        <a href="/portal/ocorrencia" className="fixed bottom-6 right-6 bg-red-600 text-white w-14 h-14 rounded-full flex items-center justify-center text-2xl shadow-lg">
          +
        </a>
      </div>
    </div>
  )
}