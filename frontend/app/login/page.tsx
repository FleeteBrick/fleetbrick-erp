"use client"

import { useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [modo, setModo] = useState<'login' | 'cadastro'>('login')
  const [empresaNome, setEmpresaNome] = useState('')
  const supabase = createClient()
  const router = useRouter()

  async function handleLogin() {
    setLoading(true)
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) {
      alert(error.message)
    } else {
      router.push('/dashboard')
    }
    setLoading(false)
  }

  async function handleCadastro() {
    if (!empresaNome) {
      alert('Digite o nome da empresa')
      return
    }
    setLoading(true)
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { nome: empresaNome } }
    })
    if (error) {
      alert(error.message)
      setLoading(false)
      return
    }
    const user = data.user
    if (user) {
      const { data: plano } = await supabase.from('planos').select('id').eq('slug', 'starter').single()
      const { data: empresa } = await supabase.from('empresas').insert({
        nome: empresaNome,
        email,
        plano_id: plano?.id,
        status_assinatura: 'trial'
      }).select().single()
      if (empresa) {
        await supabase.from('usuarios').insert({
          id: user.id,
          email,
          nome: empresaNome,
          empresa_id: empresa.id,
          role: 'admin'
        })
      }
    }
    alert('Cadastro realizado! Faça login para continuar.')
    setModo('login')
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Fleet&Brick</h1>
          <p className="text-gray-500 mt-1">Gestão de Frotas e Imóveis</p>
        </div>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setModo('login')}
            className={`flex-1 py-2 rounded-lg ${modo === 'login' ? 'bg-blue-600 text-white' : 'text-gray-500'}`}
          >
            Login
          </button>
          <button
            onClick={() => setModo('cadastro')}
            className={`flex-1 py-2 rounded-lg ${modo === 'cadastro' ? 'bg-blue-600 text-white' : 'text-gray-500'}`}
          >
            Cadastrar
          </button>
        </div>

        {modo === 'cadastro' && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome da Empresa</label>
            <input
              type="text"
              value={empresaNome}
              onChange={e => setEmpresaNome(e.target.value)}
              className="w-full border rounded-lg px-4 py-3"
              placeholder="Minha Empresa"
            />
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full border rounded-lg px-4 py-3"
              placeholder="seu@email.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Senha</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full border rounded-lg px-4 py-3"
              placeholder="••••••••"
            />
          </div>
          <button
            onClick={modo === 'login' ? handleLogin : handleCadastro}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Carregando...' : modo === 'login' ? 'Entrar' : 'Cadastrar'}
          </button>
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          Ao continuar, você concorda com nossos Termos de Uso
        </p>
      </div>
    </div>
  )
}