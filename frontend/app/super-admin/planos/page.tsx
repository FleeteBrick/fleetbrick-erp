"use client"

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'

interface Plano {
  id: string
  nome: string
  slug: string
  descricao: string
  preco: number
  max_veiculos: number
  max_imoveis: number
  max_usuarios: number
  ativo: boolean
}

export default function PlanosPage() {
  const [planos, setPlanos] = useState<Plano[]>([])
  const [loading, setLoading] = useState(true)
  const [editando, setEditando] = useState<string | null>(null)
  const [form, setForm] = useState({ preco: 0, max_veiculos: 0, max_imoveis: 0, max_usuarios: 0 })
  const supabase = createClient()

  useEffect(() => {
    carregarPlanos()
  }, [])

  async function carregarPlanos() {
    const { data } = await supabase.from('planos').select('*').order('preco')
    setPlanos(data || [])
    setLoading(false)
  }

  async function salvarPlano(plano: Plano) {
    await supabase.from('planos').update({
      preco: form.preco,
      max_veiculos: form.max_veiculos,
      max_imoveis: form.max_imoveis,
      max_usuarios: form.max_usuarios
    }).eq('id', plano.id)

    setEditando(null)
    carregarPlanos()
  }

  if (loading) return <div className="p-8 text-center">Carregando...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Planos de Assinatura</h1>
        <p className="text-gray-600 mb-8">Gerencie os planos do SaaS</p>

        <div className="grid md:grid-cols-3 gap-6">
          {planos.map(plano => (
            <div key={plano.id} className={`bg-white rounded-xl shadow-sm border p-6 ${!plano.ativo ? 'opacity-50' : ''}`}>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{plano.nome}</h3>
                  <p className="text-sm text-gray-500">{plano.descricao}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs ${plano.ativo ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                  {plano.ativo ? 'Ativo' : 'Inativo'}
                </span>
              </div>

              {editando === plano.id ? (
                <div className="space-y-4 mt-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Preço (R$)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={form.preco}
                      onChange={e => setForm({...form, preco: parseFloat(e.target.value)})}
                      className="w-full border rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Máx. Veículos</label>
                    <input
                      type="number"
                      value={form.max_veiculos}
                      onChange={e => setForm({...form, max_veiculos: parseInt(e.target.value)})}
                      className="w-full border rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Máx. Imóveis</label>
                    <input
                      type="number"
                      value={form.max_imoveis}
                      onChange={e => setForm({...form, max_imoveis: parseInt(e.target.value)})}
                      className="w-full border rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Máx. Usuários</label>
                    <input
                      type="number"
                      value={form.max_usuarios}
                      onChange={e => setForm({...form, max_usuarios: parseInt(e.target.value)})}
                      className="w-full border rounded-lg px-3 py-2"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => salvarPlano(plano)}
                      className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
                    >
                      Salvar
                    </button>
                    <button
                      onClick={() => setEditando(null)}
                      className="px-4 border py-2 rounded-lg hover:bg-gray-50"
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              ) : (
                <div className="mt-4">
                  <div className="text-3xl font-bold text-gray-900">
                    R$ {plano.preco.toFixed(2)}
                    <span className="text-sm font-normal text-gray-500">/mês</span>
                  </div>
                  <ul className="mt-4 space-y-2 text-sm text-gray-600">
                    <li className="flex justify-between">
                      <span>Veículos:</span>
                      <span className="font-medium">{plano.max_veiculos}</span>
                    </li>
                    <li className="flex justify-between">
                      <span>Imóveis:</span>
                      <span className="font-medium">{plano.max_imoveis}</span>
                    </li>
                    <li className="flex justify-between">
                      <span>Usuários:</span>
                      <span className="font-medium">{plano.max_usuarios}</span>
                    </li>
                  </ul>
                  <button
                    onClick={() => {
                      setEditando(plano.id)
                      setForm({
                        preco: plano.preco,
                        max_veiculos: plano.max_veiculos,
                        max_imoveis: plano.max_imoveis,
                        max_usuarios: plano.max_usuarios
                      })
                    }}
                    className="w-full mt-4 border py-2 rounded-lg hover:bg-gray-50"
                  >
                    Editar
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}