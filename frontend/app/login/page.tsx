"use client"

import { useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [modo, setModo] = useState<'login' | 'cadastro'>('login')
  const [nome, setNome] = useState('')
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
    setLoading(true)
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { nome } }
    })
    if (error) {
      alert(error.message)
    } else {
      alert('Cadastro realizado! Verifique seu email para confirmar.')
    }
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            <input
              type="text"
              value={nome}
              onChange={e => setNome(e.target.value)}
              className="w-full border rounded-lg px-4 py-3"
              placeholder="Seu nome"
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