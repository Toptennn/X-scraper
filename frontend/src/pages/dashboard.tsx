import { useState } from 'react'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

export default function Dashboard() {
  const [mode, setMode] = useState('timeline')
  const [authId, setAuthId] = useState('')
  const [authPass, setAuthPass] = useState('')
  const [screenName, setScreenName] = useState('')
  const [query, setQuery] = useState('')
  const [count, setCount] = useState(50)
  const [result, setResult] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const scrape = async () => {
    setLoading(true)
    const token = localStorage.getItem('token') || ''
    const payload: any = { x_auth_id: authId, x_password: authPass, mode, count }
    if (mode === 'timeline') payload.screen_name = screenName
    else payload.query = query

    const res = await fetch('http://localhost:8000/scrape/tweets', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })
    setLoading(false)
    if (res.ok) {
      const data = await res.json()
      setResult(data.tweets)
    } else {
      alert('Scrape failed')
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow p-4 space-y-4">
        <div className="space-x-2">
          <input value={authId} onChange={e => setAuthId(e.target.value)} placeholder="X Auth ID" className="border p-2" />
          <input type="password" value={authPass} onChange={e => setAuthPass(e.target.value)} placeholder="X Password" className="border p-2" />
          <select value={mode} onChange={e => setMode(e.target.value)} className="border p-2">
            <option value="timeline">Timeline</option>
            <option value="popular">Popular</option>
            <option value="latest">Latest</option>
          </select>
          {mode === 'timeline' ? (
            <input value={screenName} onChange={e => setScreenName(e.target.value)} placeholder="Screen Name" className="border p-2" />
          ) : (
            <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Query" className="border p-2" />
          )}
          <input type="number" value={count} onChange={e => setCount(parseInt(e.target.value))} className="border p-2 w-24" />
          <button onClick={scrape} className="bg-blue-600 text-white px-4 py-2" disabled={loading}>{loading ? 'Loading...' : 'Scrape'}</button>
        </div>
        <pre className="bg-gray-100 p-2 overflow-auto text-sm max-h-96">{JSON.stringify(result, null, 2)}</pre>
      </main>
      <Footer />
    </div>
  )
}
