"use client"

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useAuth } from '@/hooks/useAuth'

interface Manutencao {
  id: string
  veiculo_id: string
  tipo: string
  descricao: string
  data_agendada: string
  data_realizada: string | null
  custo: number
  status: string
  veiculos?: { placa: string }
}

export default function ManutencoesPage() {
  const [manutencoes, setManutencoes] = useState<Manutencao[]>([])
  const [veiculos, setVeiculos] = useState<{id: string, placa: string}[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState({ veiculo_id: '', tipo: 'preventiva', descricao: '', data_agendada: '', custo: '' })
  const supabase = createClient()
  const { user } = useAuth()

  useEffect(() => { if (user) carregarDados() }, [user])

  async function carregarDados() {
    if (!user) return
    const [{ data: usuario }, { data: manutData }, { data: veiculosData }] = await Promise.all([
      supabase.from('usuarios').select('empresa_id').eq('id', user.id).single(),
      supabase.from('manutencoes').select('*, veiculos(placa)').eq('empresa_id', (await supabase.from('usuarios').select('empresa_id').eq('id', user.id).single()).data?.[0]?.empresa_id || ''),
      supabase.from('veiculos').select('id, placa').eq('empresa_id', (await supabase.from('usuarios').select('empresa_id').eq('id', user.id).single()).data?.[0]?.empresa_id || '')
    ])
    setManutencoes(manutData?.filter(m => m.veiculos) || [])
    setVeiculos(veiculosData || [])
    setLoading(false)
  }

  async function salvarManutencao() {
    await supabase.from('manutencoes').insert({
      ...form,
      custo: form.custo ? parseFloat(form.custo) : null
    })
    setShowModal(false)
    setForm({ veiculo_id: '', tipo: 'preventiva', descricao: '', data_agendada: '', custo: '' })
    carregarDados()
  }

  async function completarManutencao(id: string) {
    await supabase.from('manutencoes').update({ status: 'concluida', data_realizada: new Date().toISOString().split('T')[0] }).eq('id', id)
    carregarDados()
  }

  function getStatusColor(status: string) {
    switch (status) {
      case 'agendada': return 'bg-yellow-100 text-yellow-700'
      case 'concluida': return 'bg-green-100 text-green-700'
      case 'atrasada': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  if (loading) return <div className="p-8 text-center">Carregando...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div><h1 className="text-2xl font-bold">🔧 Manutenções</h1><p className="text-gray-600">Gestão de manutenção</p></div>
          <button onClick={() => setShowModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">+ Nova Manutenção</button>
        </div>
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Veículo</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Tipo</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Descrição</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Data</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Status</th>
                <th className="text-right px-6 py-3 text-sm font-medium text-gray-500">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {manutencoes.map(m => (
                <tr key={m.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium">{m.veiculos?.placa}</td>
                  <td className="px-6 py-4">{m.tipo}</td>
                  <td className="px-6 py-4 text-sm">{m.descricao}</td>
                  <td className="px-6 py-4 text-sm">{m.data_agendada}</td>
                  <td className="px-6 py-4"><span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(m.status)}`}>{m.status}</span></td>
                  <td className="px-6 py-4 text-right">
                    {m.status === 'agendada' && <button onClick={() => completarManutencao(m.id)} className="text-green-600 hover:underline text-sm">Concluir</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {manutencoes.length === 0 && <div className="p-8 text-center text-gray-500">Nenhuma manutenção cadastrada</div>}
        </div>
      </div>
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Nova Manutenção</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Veículo *</label>
                <select value={form.veiculo_id} onChange={e => setForm({...form, veiculo_id: e.target.value})} className="w-full border rounded-lg px-3 py-2">
                  <option value="">Selecione...</option>
                  {veiculos.map(v => <option key={v.id} value={v.id}>{v.placa}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Tipo *</label>
                <select value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})} className="w-full border rounded-lg px-3 py-2">
                  <option value="preventiva">Preventiva</option>
                  <option value="corretiva">Corretiva</option>
                  <option value="troca_oleo">Troca de Óleo</option>
                  <option value="pneus">Pneus</option>
                  <option value="freios">Freios</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Descrição</label>
                <textarea value={form.descricao} onChange={e => setForm({...form, descricao: e.target.value})} rows={3} className="w-full border rounded-lg px-3 py-2" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Data Agendada *</label>
                  <input type="date" value={form.data_agendada} onChange={e => setForm({...form, data_agendada: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Custo (R$)</label>
                  <input type="number" value={form.custo} onChange={e => setForm({...form, custo: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
                </div>
              </div>
              <div className="flex gap-2">
                <button onClick={salvarManutencao} className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Salvar</button>
                <button onClick={() => setShowModal(false)} className="px-4 border rounded-lg hover:bg-gray-50">Cancelar</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}