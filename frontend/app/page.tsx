'use client'
import { useState, useEffect } from 'react'

interface TaskProgress {
  progress: number
  tweets_collected: number
  total_requested: number
  done: boolean
}

export default function Home() {
  const [auth, setAuth] = useState('')
  const [password, setPassword] = useState('')
  const [mode, setMode] = useState('timeline')
  const [query, setQuery] = useState('')
  const [screen, setScreen] = useState('')
  const [task, setTask] = useState<string | null>(null)
  const [data, setData] = useState<any[]>([])
  const [progress, setProgress] = useState<TaskProgress | null>(null)

  useEffect(() => {
    if (!task) return
    const timer = setInterval(async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/progress/${task}`,
      )
      if (res.ok) {
        const p: TaskProgress = await res.json()
        setProgress(p)
        if (p.done) {
          clearInterval(timer)
          const r = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/result/${task}`,
          )
          if (r.ok) setData(await r.json())
        }
      }
    }, 1000)
    return () => clearInterval(timer)
  }, [task])

  const start = async () => {
    const body: any = { auth, password, mode, count: 50 }
    if (mode === 'timeline') body.screen_name = screen
    else body.query = query
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/scrape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (res.ok) {
      const j = await res.json()
      setTask(j.task_id)
    }
  }

  return (
    <main className="p-4 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">X Scraper Dashboard</h1>
      <div className="space-y-2">
        <input
          className="border p-2 w-full"
          placeholder="Auth ID"
          value={auth}
          onChange={(e) => setAuth(e.target.value)}
        />
        <input
          className="border p-2 w-full"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <select
          className="border p-2 w-full"
          value={mode}
          onChange={(e) => setMode(e.target.value)}
        >
          <option value="timeline">Timeline</option>
          <option value="DATE_RANGE">Date Range</option>
          <option value="POPULAR">Popular</option>
          <option value="LATEST">Latest</option>
        </select>
        {mode === 'timeline' ? (
          <input
            className="border p-2 w-full"
            placeholder="Screen Name"
            value={screen}
            onChange={(e) => setScreen(e.target.value)}
          />
        ) : (
          <input
            className="border p-2 w-full"
            placeholder="Query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        )}
        <button className="bg-blue-500 text-white px-4 py-2" onClick={start}>
          Start
        </button>
      </div>
      {progress && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 h-2 rounded">
            <div
              className="bg-blue-500 h-2 rounded"
              style={{ width: `${progress.progress * 100}%` }}
            ></div>
          </div>
          <p>
            {progress.tweets_collected}/{progress.total_requested}
          </p>
        </div>
      )}
      {data.length > 0 && (
        <pre className="mt-4 bg-gray-100 p-2 overflow-x-auto text-xs">
          {JSON.stringify(data.slice(0, 3), null, 2)}...
        </pre>
      )}
    </main>
  )
}
