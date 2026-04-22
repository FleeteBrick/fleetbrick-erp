"use client"

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useAuth } from '@/hooks/useAuth'

interface Veiculo {
  id: string
  placa: string
  marca: string
  modelo: string
  ano: number
  cor: string
  tipo_combustivel: string
  quilometragem_atual: number
  status: string
}

export default function VeiculosPage() {
  const [veiculos, setVeiculos] = useState<Veiculo[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({
    placa: '', marca: '', modelo: '', ano: '', cor: '', tipo_combustivel: 'flex', quilometragem_atual: ''
  })
  const supabase = createClient()
  const { user } = useAuth()

  useEffect(() => {
    if (user) carregarVeiculos()
  }, [user])

  async function carregarVeiculos() {
    if (!user) return
    const { data: usuario } = await supabase.from('usuarios').select('empresa_id').eq('id', user.id).single()
    if (!usuario) return

    const { data } = await supabase.from('veiculos').select('*').eq('empresa_id', usuario.empresa_id).order('created_at', { ascending: false })
    setVeiculos(data || [])
    setLoading(false)
  }

  async function salvarVeiculo() {
    await supabase.from('veiculos').insert({
      ...form,
      ano: form.ano ? parseInt(form.ano) : null,
      quilometragem_atual: form.quilometragem_atual ? parseInt(form.quilometragem_atual) : 0
    })
    setShowModal(false)
    setForm({ placa: '', marca: '', modelo: '', ano: '', cor: '', tipo_combustivel: 'flex', quilometragem_atual: '' })
    carregarVeiculos()
  }

  async function excluirVeiculo(id: string) {
    if (confirm('Tem certeza que deseja remover este veículo?')) {
      await supabase.from('veiculos').update({ status: 'vendido' }).eq('id', id)
      carregarVeiculos()
    }
  }

  function getStatusColor(status: string) {
    switch (status) {
      case 'ativo': return 'bg-green-100 text-green-700'
      case 'em_rota': return 'bg-blue-100 text-blue-700'
      case 'manutencao': return 'bg-yellow-100 text-yellow-700'
      case 'vendido': return 'bg-gray-100 text-gray-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  if (loading) return <div className="p-8 text-center">Carregando...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold">🚛 Veículos</h1>
            <p className="text-gray-600">Gestão de fretas</p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            + Novo Veículo
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Placa</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Veículo</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">KM</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Status</th>
                <th className="text-right px-6 py-3 text-sm font-medium text-gray-500">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {veiculos.map(veiculo => (
                <tr key={veiculo.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium">{veiculo.placa}</td>
                  <td className="px-6 py-4">
                    <p className="font-medium">{veiculo.marca} {veiculo.modelo}</p>
                    <p className="text-sm text-gray-500">{veiculo.ano} • {veiculo.cor}</p>
                  </td>
                  <td className="px-6 py-4">{veiculo.quilometragem_atual?.toLocaleString()} km</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(veiculo.status)}`}>
                      {veiculo.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button onClick={() => excluirVeiculo(veiculo.id)} className="text-red-600 hover:underline text-sm">
                      Remover
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {veiculos.length === 0 && (
            <div className="p-8 text-center text-gray-500">Nenhum veículo cadastrado</div>
          )}
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Novo Veículo</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Placa *</label>
                <input
                  value={form.placa}
                  onChange={e => setForm({...form, placa: e.target.value.toUpperCase()})}
                  className="w-full border rounded-lg px-3 py-2"
                  placeholder="ABC-1234"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Marca</label>
                  <input
                    value={form.marca}
                    onChange={e => setForm({...form, marca: e.target.value})}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Modelo</label>
                  <input
                    value={form.modelo}
                    onChange={e => setForm({...form, modelo: e.target.value})}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Ano</label>
                  <input
                    type="number"
                    value={form.ano}
                    onChange={e => setForm({...form, ano: e.target.value})}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Cor</label>
                  <input
                    value={form.cor}
                    onChange={e => setForm({...form, cor: e.target.value})}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">KM</label>
                  <input
                    type="number"
                    value={form.quilometragem_atual}
                    onChange={e => setForm({...form, quilometragem_atual: e.target.value})}
                    className="w-full border rounded-lg px-3 py-2"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Combustível</label>
                <select
                  value={form.tipo_combustivel}
                  onChange={e => setForm({...form, tipo_combustivel: e.target.value})}
                  className="w-full border rounded-lg px-3 py-2"
                >
                  <option value="flex">Flex</option>
                  <option value="gasolina">Gasolina</option>
                  <option value="diesel">Diesel</option>
                  <option value="eletrico">Elétrico</option>
                </select>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={salvarVeiculo}
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
                >
                  Salvar
                </button>
                <button
                  onClick={() => setShowModal(false)}
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