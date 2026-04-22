import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase'

export default function Home() {
  const supabase = createClient()
  
  async function checkAuth() {
    const { data: { user } } = await supabase.auth.getUser()
    if (user) {
      redirect('/dashboard')
    } else {
      redirect('/login')
    }
  }
  
  checkAuth()
  
  return (
    <div className="min-h-screen flex items-center justify-center">
      <p>Carregando...</p>
    </div>
  )
}