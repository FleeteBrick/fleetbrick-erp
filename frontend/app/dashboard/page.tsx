"use client"

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useAuth } from '@/hooks/useAuth'

interface Stats {
  propriedades_ocupadas: number
  propriedades_totais: number
  veiculos_rota: number
  veiculos_totais: number
  receita_mensal: number
  plano: {
    nome: string
    max_veiculos: number
    max_imoveis: number
  }
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats>({
    propriedades_ocupadas: 0,
    propriedades_totais: 0,
    veiculos_rota: 0,
    veiculos_totais: 0,
    receita_mensal: 0,
    plano: { nome: '', max_veiculos: 0, max_imoveis: 0 }
  })
  const [loading, setLoading] = useState(true)
  const [showFeedback, setShowFeedback] = useState(false)
  const [feedback, setFeedback] = useState({ titulo: '', descricao: '', tipo: 'suporte' })
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

    if (!usuario?.empresa_id) {
      setLoading(false)
      return
    }
    
    const { data: emp } = await supabase.from('empresas').select('plano_id').eq('id', usuario.empresa_id).single()
    const { data: propriedades } = await supabase.from('propriedades').select('*').eq('empresa_id', usuario.empresa_id)
    const { data: veiculos } = await supabase.from('veiculos').select('*').eq('empresa_id', usuario.empresa_id)
    
    let plano = { nome: 'Starter', max_veiculos: 5, max_imoveis: 10 }
    if (emp?.plano_id) {
      const { data: p } = await supabase.from('planos').select('*').eq('id', emp.plano_id).single()
      if (p) plano = p
    }

    const propsOcupadas = propriedades?.filter(p => p.status === 'alugado').length || 0
    const veiculosRota = veiculos?.filter(v => v.status === 'em_rota').length || 0

    setStats({
      propriedades_ocupadas: propsOcupadas,
      propriedades_totais: propriedades?.length || 0,
      veiculos_rota: veiculosRota,
      veiculos_totais: veiculos?.length || 0,
      receita_mensal: propsOcupadas * 1500,
      plano: plano || { nome: 'Starter', max_veiculos: 5, max_imoveis: 10 }
    })
    setLoading(false)
  }

  async function enviarFeedback() {
    await supabase.from('chamados_suporte').insert({
      tipo: feedback.tipo,
      titulo: feedback.titulo,
      descricao: feedback.descricao
    })
    setShowFeedback(false)
    setFeedback({ titulo: '', descricao: '', tipo: 'suporte' })
    alert('Feedback enviado com sucesso!')
  }

  if (loading) return <div className="p-8 text-center">Carregando...</div>

  const ocupacaoVeiculos = (stats.veiculos_totais / stats.plano.max_veiculos) * 100
  const ocupacaoImoveis = (stats.propriedades_totais / stats.plano.max_imoveis) * 100

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b px-8 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">Fleet&Brick</h1>
          <button
            onClick={() => setShowFeedback(true)}
            className="text-sm text-blue-600 hover:underline"
          >
            Feedback
          </button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-1">Dashboard</h2>
        <p className="text-gray-600 mb-8">{stats.plano.nome}</p>

        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <p className="text-sm text-gray-500">Imóveis Ocupados</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">
              {stats.propriedades_ocupadas}
              <span className="text-lg font-normal text-gray-500">/{stats.propriedades_totais}</span>
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <p className="text-sm text-gray-500">Veículos em Rota</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">
              {stats.veiculos_rota}
              <span className="text-lg font-normal text-gray-500">/{stats.veiculos_totais}</span>
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <p className="text-sm text-gray-500">Receita Mensal</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">
              R$ {stats.receita_mensal.toLocaleString('pt-BR')}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <p className="text-sm text-gray-500">Chamados Abertos</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">0</p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="font-bold text-gray-900 mb-4">Consumo do Plano</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Veículos</span>
                  <span>{stats.veiculos_totais}/{stats.plano.max_veiculos}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${ocupacaoVeiculos > 80 ? 'bg-red-500' : ocupacaoVeiculos > 60 ? 'bg-yellow-500' : 'bg-blue-600'}`}
                    style={{ width: `${Math.min(ocupacaoVeiculos, 100)}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Imóveis</span>
                  <span>{stats.propriedades_totais}/{stats.plano.max_imoveis}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${ocupacaoImoveis > 80 ? 'bg-red-500' : ocupacaoImoveis > 60 ? 'bg-yellow-500' : 'bg-blue-600'}`}
                    style={{ width: `${Math.min(ocupacaoImoveis, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="font-bold text-gray-900 mb-4">Ações Rápidas</h3>
            <div className="grid grid-cols-2 gap-3">
              <a href="/propriedades" className="border rounded-lg p-4 text-center hover:bg-gray-50">
                <p className="text-2xl mb-1">🏢</p>
                <p className="text-sm">Imóveis</p>
              </a>
              <a href="/veiculos" className="border rounded-lg p-4 text-center hover:bg-gray-50">
                <p className="text-2xl mb-1">🚛</p>
                <p className="text-sm">Veículos</p>
              </a>
              <a href="/contratos" className="border rounded-lg p-4 text-center hover:bg-gray-50">
                <p className="text-2xl mb-1">📄</p>
                <p className="text-sm">Contratos</p>
              </a>
              <a href="/manutencoes" className="border rounded-lg p-4 text-center hover:bg-gray-50">
                <p className="text-2xl mb-1">🔧</p>
                <p className="text-sm">Manutenção</p>
              </a>
            </div>
          </div>
        </div>
      </div>

      {showFeedback && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Enviar Feedback</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Tipo</label>
                <select
                  value={feedback.tipo}
                  onChange={e => setFeedback({...feedback, tipo: e.target.value})}
                  className="w-full border rounded-lg px-3 py-2"
                >
                  <option value="suporte">Suporte</option>
                  <option value="bug">Bug</option>
                  <option value="sugestao">Sugestão</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Título</label>
                <input
                  value={feedback.titulo}
                  onChange={e => setFeedback({...feedback, titulo: e.target.value})}
                  className="w-full border rounded-lg px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Descrição</label>
                <textarea
                  value={feedback.descricao}
                  onChange={e => setFeedback({...feedback, descricao: e.target.value})}
                  rows={4}
                  className="w-full border rounded-lg px-3 py-2"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={enviarFeedback}
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
                >
                  Enviar
                </button>
                <button
                  onClick={() => setShowFeedback(false)}
                  className="px-4 border rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}