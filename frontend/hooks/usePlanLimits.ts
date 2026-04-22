"use client"

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'

interface PlanLimits {
  nome: string
  preco: number
  max_veiculos: number
  max_imoveis: number
  max_usuarios: number
  veiculos_usados: number
  imoveis_usados: number
  usuarios_usados: number
  loading: boolean
}

export function usePlanLimits() {
  const [limits, setLimits] = useState<PlanLimits>({
    nome: '',
    preco: 0,
    max_veiculos: 0,
    max_imoveis: 0,
    max_usuarios: 0,
    veiculos_usados: 0,
    imoveis_usados: 0,
    usuarios_usados: 0,
    loading: true
  })

  const supabase = createClient()

  useEffect(() => {
    const fetchLimits = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return

      const { data: usuario } = await supabase
        .from('usuarios')
        .select('empresa_id')
        .eq('id', user.id)
        .single()

      if (!usuario) return

      const { data: empresa } = await supabase
        .from('empresas')
        .select('plano_id, planos(*)')
        .eq('id', usuario.empresa_id)
        .single()

      if (!empresa) return

      const [{ count: veiculos }, { count: imoveis }, { count: usuarios }] = await Promise.all([
        supabase.from('veiculos').select('*', { count: 'exact' }).eq('empresa_id', usuario.empresa_id).neq('status', 'vendido'),
        supabase.from('imoveis').select('*', { count: 'exact' }).eq('empresa_id', usuario.empresa_id).neq('status', 'vendido'),
        supabase.from('usuarios').select('*', { count: 'exact' }).eq('empresa_id', usuario.empresa_id).eq('ativo', true)
      ])

      setLimits({
        nome: (empresa.planos as any)?.nome || '',
        preco: (empresa.planos as any)?.preco || 0,
        max_veiculos: (empresa.planos as any)?.max_veiculos || 0,
        max_imoveis: (empresa.planos as any)?.max_imoveis || 0,
        max_usuarios: (empresa.planos as any)?.max_usuarios || 0,
        veiculos_usados: veiculos || 0,
        imoveis_usados: imoveis || 0,
        usuarios_usados: usuarios || 0,
        loading: false
      })
    }

    fetchLimits()
  }, [supabase])

  return limits
}
