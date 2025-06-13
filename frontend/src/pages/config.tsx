import { useEffect, useState } from 'react'

export default function Config() {
  const [manuals, setManuals] = useState<string[]>([])
  const [file, setFile] = useState<File | null>(null)

  const fetchManuals = async () => {
    const res = await fetch('http://localhost:8000/manuals')
    const data = await res.json()
    setManuals(data.files as string[])
  }

  const deleteManual = async (filename: string) => {
    await fetch(`http://localhost:8000/manuals/${encodeURIComponent(filename)}`, {
      method: 'DELETE',
    })
    fetchManuals()
  }

  useEffect(() => {
    fetchManuals()
  }, [])

  const upload = async () => {
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    await fetch('http://localhost:8000/manuals', { method: 'POST', body: form })
    setFile(null)
    fetchManuals()
  }

  return (
    <div className="container">
      <h1>Files to Training Security Chatbot</h1>
      <div>
        <input type="file" accept="application/pdf" onChange={e => setFile(e.target.files?.[0] ?? null)} />
        <button onClick={upload}>Add manual</button>
      </div>
      <ul>
        {manuals.map(m => (
          <li key={m} className="manual-item">
            <span className="pdf-icon">📄</span> {m}
            <button onClick={() => deleteManual(m)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
