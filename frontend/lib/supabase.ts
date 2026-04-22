import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { Database } from '@/types/database'

export const createClient = () => {
  return createClientComponentClient<Database>()
}

export const getServiceRoleClient = () => {
  // Usar apenas no servidor (Server Components/Actions)
  return createClientComponentClient<Database>({
    supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL!,
    supabaseKey: process.env.SUPABASE_SERVICE_KEY!
  })
}
