"use client"

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useAuth } from '@/hooks/useAuth'

interface Propriedade {
  id: string
  codigo_interno: string
  endereco: string
  cidade: string
  estado: string
  tipo: string
  status: string
  valor_aluguel: number
  area_m2: number
  quartos: number
  banheiros: number
}

export default function PropriedadesPage() {
  const [propriedades, setPropriedades] = useState<Propriedade[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [filtro, setFiltro] = useState('todos')
  const [form, setForm] = useState({
    codigo_interno: '', endereco: '', cidade: '', estado: '', tipo: 'apartamento',
    valor_aluguel: '', area_m2: '', quartos: '', banheiros: '', descricao: ''
  })
  const supabase = createClient()
  const { user } = useAuth()

  useEffect(() => {
    if (user) carregarPropriedades()
  }, [user, filtro])

  async function carregarPropriedades() {
    if (!user) return
    const { data: usuario } = await supabase.from('usuarios').select('empresa_id').eq('id', user.id).single()
    if (!usuario) return

    let query = supabase.from('propriedades').select('*').eq('empresa_id', usuario.empresa_id)
    if (filtro !== 'todos') query = query.eq('status', filtro)
    
    const { data } = await query.order('created_at', { ascending: false })
    setPropriedades(data || [])
    setLoading(false)
  }

  async function salvarPropriedade() {
    await supabase.from('propriedades').insert({
      ...form,
      valor_aluguel: form.valor_aluguel ? parseFloat(form.valor_aluguel) : null,
      area_m2: form.area_m2 ? parseFloat(form.area_m2) : null,
      quartos: form.quartos ? parseInt(form.quartos) : null,
      banheiros: form.banheiros ? parseInt(form.banheiros) : null
    })
    setShowModal(false)
    setForm({ codigo_interno: '', endereco: '', cidade: '', estado: '', tipo: 'apartamento', valor_aluguel: '', area_m2: '', quartos: '', banheiros: '', descricao: '' })
    carregarPropriedades()
  }

  function getStatusColor(status: string) {
    switch (status) {
      case 'livre': return 'bg-green-100 text-green-700'
      case 'alugado': return 'bg-blue-100 text-blue-700'
      case 'manutencao': return 'bg-yellow-100 text-yellow-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  if (loading) return <div className="p-8 text-center">Carregando...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold">🏢 Imóveis</h1>
            <p className="text-gray-600">Gestão de propriedades</p>
          </div>
          <button onClick={() => setShowModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            + Novo Imóvel
          </button>
        </div>

        <div className="flex gap-2 mb-4">
          {['todos', 'livre', 'alugado', 'manutencao'].map(s => (
            <button
              key={s}
              onClick={() => setFiltro(s)}
              className={`px-4 py-2 rounded-lg text-sm ${filtro === s ? 'bg-blue-600 text-white' : 'bg-white border hover:bg-gray-50'}`}
            >
              {s === 'todos' ? 'Todos' : s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {propriedades.map(prop => (
            <div key={prop.id} className="bg-white rounded-xl shadow-sm border p-4">
              <div className="flex justify-between items-start mb-2">
                <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(prop.status)}`}>
                  {prop.status}
                </span>
                {prop.codigo_interno && <span className="text-xs text-gray-500">#{prop.codigo_interno}</span>}
              </div>
              <h3 className="font-medium text-gray-900">{prop.endereco}</h3>
              <p className="text-sm text-gray-500">{prop.cidade} - {prop.estado}</p>
              <div className="mt-3 flex gap-4 text-sm text-gray-600">
                {prop.area_m2 && <span>{prop.area_m2} m²</span>}
                {prop.quartos && <span>{prop.quartos} quartos</span>}
                {prop.banheiros && <span>{prop.banheiros} banheiros</span>}
              </div>
              {prop.valor_aluguel && (
                <p className="mt-2 font-bold text-lg">R$ {prop.valor_aluguel.toLocaleString('pt-BR')}<span className="text-sm font-normal text-gray-500">/mês</span></p>
              )}
            </div>
          ))}
        </div>
        {propriedades.length === 0 && (
          <div className="bg-white rounded-xl border p-8 text-center text-gray-500">Nenhum imóvel cadastrado</div>
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold mb-4">Nova Propriedade</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Endereço *</label>
                <input value={form.endereco} onChange={e => setForm({...form, endereco: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Cidade</label>
                  <input value={form.cidade} onChange={e => setForm({...form, cidade: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Estado</label>
                  <input value={form.estado} onChange={e => setForm({...form, estado: e.target.value.toUpperCase()})} maxLength={2} className="w-full border rounded-lg px-3 py-2" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Tipo</label>
                  <select value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})} className="w-full border rounded-lg px-3 py-2">
                    <option value="apartamento">Apartamento</option>
                    <option value="casa">Casa</option>
                    <option value="galpao">Galpão</option>
                    <option value="sala">Sala Comercial</option>
                    <option value="loja">Loja</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Valor Aluguel (R$)</label>
                  <input type="number" value={form.valor_aluguel} onChange={e => setForm({...form, valor_aluguel: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Área (m²)</label>
                  <input type="number" value={form.area_m2} onChange={e => setForm({...form, area_m2: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Quartos</label>
                  <input type="number" value={form.quartos} onChange={e => setForm({...form, quartos: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Banheiros</label>
                  <input type="number" value={form.banheiros} onChange={e => setForm({...form, banheiros: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
                </div>
              </div>
              <div className="flex gap-2">
                <button onClick={salvarPropriedade} className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Salvar</button>
                <button onClick={() => setShowModal(false)} className="px-4 border rounded-lg hover:bg-gray-50">Cancelar</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}