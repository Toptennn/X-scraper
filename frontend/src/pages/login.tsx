import { useState } from 'react'
import { useRouter } from 'next/router'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleLogin = async () => {
    setLoading(true)
    const res = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })
    setLoading(false)
    if (res.ok) {
      const data = await res.json()
      localStorage.setItem('token', data.access_token)
      router.push('/dashboard')
    } else {
      alert('Login failed')
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow flex items-center justify-center">
        <div className="w-full max-w-md space-y-4 p-6 bg-white rounded shadow">
          <h2 className="text-2xl font-bold text-center">Login</h2>
          <input className="w-full border p-2" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
          <input className="w-full border p-2" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
          <button onClick={handleLogin} className="w-full bg-blue-600 text-white py-2" disabled={loading}>{loading ? 'Loading...' : 'Login'}</button>
        </div>
      </main>
      <Footer />
    </div>
  )
}
