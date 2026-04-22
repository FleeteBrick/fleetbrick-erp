"use client"

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useAuth } from '@/hooks/useAuth'

interface Contrato {
  id: string
  propriedade_id: string
  inquilino_nome: string
  inquilino_email: string
  inquilino_telefone: string
  data_entrada: string
  data_inicio_contrato: string
  valor_aluguel: number
  dia_vencimento: number
  status: string
  propriedades?: { endereco: string }
}

export default function ContratosPage() {
  const [contratos, setContratos] = useState<Contrato[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [propriedades, setPropriedades] = useState<{id: string, endereco: string}[]>([])
  const [form, setForm] = useState({
    propriedade_id: '',
    inquilino_nome: '',
    inquilino_email: '',
    inquilino_telefone: '',
    data_inicio_contrato: '',
    data_fim_contrato: '',
    valor_aluguel: '',
    dia_vencimento: '5'
  })
  const supabase = createClient()
  const { user } = useAuth()

  useEffect(() => {
    if (user) carregarDados()
  }, [user])

  async function carregarDados() {
    if (!user) return
    const { data: usuario } = await supabase.from('usuarios').select('empresa_id').eq('id', user.id).single()
    if (!usuario) return

    const [contratosData, propriedadesData] = await Promise.all([
      supabase.from('contratos_locacao').select('*, propriedades(endereco)').eq('empresa_id', usuario.empresa_id).order('created_at', { ascending: false }),
      supabase.from('propriedades').select('id, endereco').eq('empresa_id', usuario.empresa_id).eq('status', 'livre')
    ])

    setContratos(contratosData.data || [])
    setPropriedades(propriedadesData.data || [])
    setLoading(false)
  }

  async function salvarContrato() {
    await supabase.from('contratos_locacao').insert({
      ...form,
      data_entrada: form.data_inicio_contrato,
      valor_aluguel: parseFloat(form.valor_aluguel),
      dia_vencimento: parseInt(form.dia_vencimento)
    })
    setShowModal(false)
    setForm({ propriedade_id: '', inquilino_nome: '', inquilino_email: '', inquilino_telefone: '', data_inicio_contrato: '', data_fim_contrato: '', valor_aluguel: '', dia_vencimento: '5' })
    carregarDados()
  }

  async function encerrarContrato(id: string) {
    if (confirm('Encerrar este contrato?')) {
      await supabase.from('contratos_locacao').update({ status: 'encerrado' }).eq('id', id)
      carregarDados()
    }
  }

  if (loading) return <div className="p-8 text-center">Carregando...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold">📄 Contratos</h1>
            <p className="text-gray-600">Gestão de locações</p>
          </div>
          <button onClick={() => setShowModal(true)} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            + Novo Contrato
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Inquilino</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Imóvel</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Valor</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Entrada</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-500">Status</th>
                <th className="text-right px-6 py-3 text-sm font-medium text-gray-500">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {contratos.map(contrato => (
                <tr key={contrato.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <p className="font-medium">{contrato.inquilino_nome}</p>
                    <p className="text-sm text-gray-500">{contrato.inquilino_email}</p>
                  </td>
                  <td className="px-6 py-4 text-sm">{contrato.propriedades?.endereco}</td>
                  <td className="px-6 py-4 font-medium">R$ {contrato.valor_aluguel?.toLocaleString('pt-BR')}</td>
                  <td className="px-6 py-4 text-sm">{new Date(contrato.data_entrada).toLocaleDateString('pt-BR')}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${contrato.status === 'ativo' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                      {contrato.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {contrato.status === 'ativo' && (
                      <button onClick={() => encerrarContrato(contrato.id)} className="text-red-600 hover:underline text-sm">
                        Encerrar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {contratos.length === 0 && (
            <div className="p-8 text-center text-gray-500">Nenhum contrato cadastrado</div>
          )}
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-bold mb-4">Novo Contrato</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Imóvel *</label>
                <select value={form.propriedade_id} onChange={e => setForm({...form, propriedade_id: e.target.value})} className="w-full border rounded-lg px-3 py-2">
                  <option value="">Selecione...</option>
                  {propriedades.map(p => <option key={p.id} value={p.id}>{p.endereco}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Nome do Inquilino *</label>
                <input value={form.inquilino_nome} onChange={e => setForm({...form, inquilino_nome: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <input type="email" value={form.inquilino_email} onChange={e => setForm({...form, inquilino_email: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Telefone</label>
                <input value={form.inquilino_telefone} onChange={e => setForm({...form, inquilino_telefone: e.target.value})} className="w-full border rounded-lg px-3 py-2" placeholder="(11) 99999-9999" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Data Início *</label>
                  <input type="date" value={form.data_inicio_contrato} onChange={e => setForm({...form, data_inicio_contrato: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Dia Vencimento</label>
                  <input type="number" value={form.dia_vencimento} onChange={e => setForm({...form, dia_vencimento: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Valor Aluguel (R$) *</label>
                <input type="number" value={form.valor_aluguel} onChange={e => setForm({...form, valor_aluguel: e.target.value})} className="w-full border rounded-lg px-3 py-2" />
              </div>
              <div className="flex gap-2">
                <button onClick={salvarContrato} className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">Salvar</button>
                <button onClick={() => setShowModal(false)} className="px-4 border rounded-lg hover:bg-gray-50">Cancelar</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}