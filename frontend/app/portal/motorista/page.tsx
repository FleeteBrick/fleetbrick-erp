"use client"

import { useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'

export default function MotoristaPage() {
  const [step, setStep] = useState(1)
  const [form, setForm] = useState({
    km_inicial: '',
    avarias: '',
    litros: '',
    valor: '',
    nota_url: ''
  })
  const [loading, setLoading] = useState(false)
  const supabase = createClient()
  const router = useRouter()

  async function submeterCheckin() {
    setLoading(true)
    await supabase.from('checklists_vistoria').insert({
      tipo: 'checkin',
      km_inicial: parseInt(form.km_inicial),
      obs: form.avarias,
      itens: JSON.stringify({})
    })
    setStep(2)
    setLoading(false)
  }

  async function submeterAbastecimento() {
    setLoading(true)
    await supabase.from('abastecimentos').insert({
      litros: parseFloat(form.litros),
      valor: parseFloat(form.valor),
      nota_fiscal_url: form.nota_url
    })
    alert('Abasteecimento registrado!')
    router.push('/')
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-md mx-auto p-4">
        <h1 className="text-2xl font-bold text-center mb-6">🚛 Portal Motorista</h1>

        {step === 1 && (
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-lg font-bold mb-4">Check-in Diário</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Km Inicial</label>
                <input
                  type="number"
                  value={form.km_inicial}
                  onChange={e => setForm({...form, km_inicial: e.target.value})}
                  className="w-full border rounded-lg px-4 py-3"
                  placeholder="Digite a quilometragem atual"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Relato de Avarias</label>
                <textarea
                  value={form.avarias}
                  onChange={e => setForm({...form, avarias: e.target.value})}
                  className="w-full border rounded-lg px-4 py-3"
                  rows={3}
                  placeholder="Descreva avarias encontradas..."
                />
              </div>

              <button
                onClick={submeterCheckin}
                disabled={loading || !form.km_inicial}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium disabled:opacity-50"
              >
                {loading ? 'Enviando...' : 'Confirmar Check-in'}
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-lg font-bold mb-4">Registrar Abastecimento</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Litros</label>
                <input
                  type="number"
                  step="0.001"
                  value={form.litros}
                  onChange={e => setForm({...form, litros: e.target.value})}
                  className="w-full border rounded-lg px-4 py-3"
                  placeholder="Quantos litros?"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-1">Valor (R$)</label>
                <input
                  type="number"
                  step="0.01"
                  value={form.valor}
                  onChange={e => setForm({...form, valor: e.target.value})}
                  className="w-full border rounded-lg px-4 py-3"
                  placeholder="Valor total"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Foto da Nota (opcional)</label>
                <input
                  type="url"
                  value={form.nota_url}
                  onChange={e => setForm({...form, nota_url: e.target.value})}
                  className="w-full border rounded-lg px-4 py-3"
                  placeholder="URL da imagem"
                />
              </div>

              <button
                onClick={submeterAbastecimento}
                disabled={loading || !form.litros || !form.valor}
                className="w-full bg-green-600 text-white py-3 rounded-lg font-medium disabled:opacity-50"
              >
                {loading ? 'Enviando...' : 'Registrar Abastecimento'}
              </button>

              <button
                onClick={() => router.push('/')}
                className="w-full border py-3 rounded-lg"
              >
                Pular
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}