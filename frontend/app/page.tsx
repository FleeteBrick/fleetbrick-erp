import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex flex-col items-center justify-center p-4">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-white mb-4">Fleet&Brick v2</h1>
        <p className="text-xl text-slate-300">Sistema de Gestão de Frotas e Imóveis</p>
      </div>
      <div className="flex gap-4">
        <Link href="/login" className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-blue-700">
          Login
        </Link>
        <Link href="/dashboard" className="bg-white text-slate-900 px-8 py-3 rounded-lg text-lg font-medium hover:bg-slate-100">
          Dashboard
        </Link>
      </div>
    </div>
  )
}