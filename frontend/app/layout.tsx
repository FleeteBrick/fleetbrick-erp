"use client"

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { createClient } from '@/lib/supabase'
import { useAuth } from '@/hooks/useAuth'

export default function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { user, signOut } = useAuth()
  const [empresa, setEmpresa] = useState<{nome: string} | null>(null)
  const supabase = createClient()

  useEffect(() => {
    if (user) buscarEmpresa()
  }, [user])

  async function buscarEmpresa() {
    if (!user) return
    const { data } = await supabase.from('usuarios').select('empresa_id').eq('id', user.id).single()
    if (data) {
      const { data: emp } = await supabase.from('empresas').select('nome').eq('id', data.empresa_id).single()
      setEmpresa(emp)
    }
  }

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    { href: '/propriedades', label: 'Imóveis', icon: '🏢' },
    { href: '/veiculos', label: 'Veículos', icon: '🚛' },
    { href: '/contratos', label: 'Contratos', icon: '📄' },
  ]

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50">
        {children}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-64 bg-white border-r fixed h-full">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold">Fleet&Brick</h1>
          <p className="text-sm text-gray-500">{empresa?.nome || 'Carregando...'}</p>
        </div>
        <nav className="p-2">
          {navItems.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg mb-1 ${
                pathname === item.href ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
        <div className="absolute bottom-0 w-64 p-4 border-t">
          <button
            onClick={signOut}
            className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
          >
            Sair
          </button>
        </div>
      </aside>
      <main className="flex-1 ml-64">
        {children}
      </main>
    </div>
  )
}