import './globals.css'

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center p-8">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">Fleet&Brick</h1>
        <p className="text-xl text-gray-600 mb-8">Sistema de Gestão de Frotas e Imóveis</p>
        <div className="flex gap-4 justify-center">
          <a href="/login" className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
            Login
          </a>
          <a href="/dashboard" className="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300">
            Dashboard
          </a>
        </div>
      </div>
    </main>
  )
}