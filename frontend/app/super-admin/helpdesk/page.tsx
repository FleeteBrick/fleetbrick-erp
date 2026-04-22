"use client"

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'

interface Chamado {
  id: string
  empresa_id: string
  tipo: string
  titulo: string
  descricao: string
  nivel_prioridade: string
  status: string
  categoria: string
  created_at: string
}

export default function HelpdeskPage() {
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    carregarChamados()
  }, [])

  async function carregarChamados() {
    const { data } = await supabase
      .from('chamados_suporte')
      .select('*')
      .order('created_at', { ascending: false })
    
    setChamados(data || [])
    setLoading(false)
  }

  const chamadosPorCategoria = {
    bugs: chamados.filter(c => c.categoria === 'bug'),
    sugestoes: chamados.filter(c => c.categoria === 'sugestao'),
    suporte: chamados.filter(c => c.categoria === 'duvida' || !c.categoria)
  }

  function getPrioridadeCor(nivel: string) {
    switch (nivel) {
      case 'critica': return 'bg-red-100 text-red-700'
      case 'alta': return 'bg-orange-100 text-orange-700'
      case 'media': return 'bg-yellow-100 text-yellow-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  async function resolverChamado(id: string) {
    await supabase.from('chamados_suporte').update({
      status: 'resolvido'
    }).eq('id', id)
    carregarChamados()
  }

  if (loading) return <div className="p-8 text-center">Carregando...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Central de Helpdesk</h1>
        <p className="text-gray-600 mb-8">Triagem automática de tickets</p>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Bugs */}
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-4 border-b bg-red-50">
              <h2 className="font-bold text-red-700">🐛 Bugs ({chamadosPorCategoria.bugs.length})</h2>
            </div>
            <div className="p-4 space-y-3 min-h-[400px]">
              {chamadosPorCategoria.bugs.map(chamado => (
                <div key={chamado.id} className="border rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${getPrioridadeCor(chamado.nivel_prioridade)}`}>
                      {chamado.nivel_prioridade}
                    </span>
                    <span className="text-xs text-gray-500">{new Date(chamado.created_at).toLocaleDateString()}</span>
                  </div>
                  <h4 className="font-medium text-gray-900">{chamado.titulo}</h4>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{chamado.descricao}</p>
                  <button
                    onClick={() => resolverChamado(chamado.id)}
                    className="mt-2 text-sm text-blue-600 hover:underline"
                  >
                    Resolver
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Sugestões */}
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-4 border-b bg-purple-50">
              <h2 className="font-bold text-purple-700">💡 Sugestões ({chamadosPorCategoria.sugestoes.length})</h2>
            </div>
            <div className="p-4 space-y-3 min-h-[400px]">
              {chamadosPorCategoria.sugestoes.map(chamado => (
                <div key={chamado.id} className="border rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${getPrioridadeCor(chamado.nivel_prioridade)}`}>
                      {chamado.nivel_prioridade}
                    </span>
                    <span className="text-xs text-gray-500">{new Date(chamado.created_at).toLocaleDateString()}</span>
                  </div>
                  <h4 className="font-medium text-gray-900">{chamado.titulo}</h4>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{chamado.descricao}</p>
                  <button
                    onClick={() => resolverChamado(chamado.id)}
                    className="mt-2 text-sm text-blue-600 hover:underline"
                  >
                    Resolver
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Suporte */}
          <div className="bg-white rounded-xl shadow-sm border">
            <div className="p-4 border-b bg-blue-50">
              <h2 className="font-bold text-blue-700">❓ Suporte ({chamadosPorCategoria.suporte.length})</h2>
            </div>
            <div className="p-4 space-y-3 min-h-[400px]">
              {chamadosPorCategoria.suporte.map(chamado => (
                <div key={chamado.id} className="border rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${getPrioridadeCor(chamado.nivel_prioridade)}`}>
                      {chamado.nivel_prioridade}
                    </span>
                    <span className="text-xs text-gray-500">{new Date(chamado.created_at).toLocaleDateString()}</span>
                  </div>
                  <h4 className="font-medium text-gray-900">{chamado.titulo}</h4>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{chamado.descricao}</p>
                  <button
                    onClick={() => resolverChamado(chamado.id)}
                    className="mt-2 text-sm text-blue-600 hover:underline"
                  >
                    Resolver
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}