/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost', 'guzzdpvrcslpqejnansv.supabase.co'],
  },
  env: {
    NEXT_PUBLIC_SUPABASE_URL: 'https://guzzdpvrcslpqejnansv.supabase.co',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: 'sb_publishable_jH6QfBHQDNX5We_u5XYE7w_LMu3aLxk',
  },
}

module.exports = nextConfig
