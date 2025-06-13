import { useEffect, useState } from 'react'
import { trpc } from '../utils/trpc'

const baseURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default function Config() {
  const manualsQuery = trpc.listManuals.useQuery()
  const deleteManual = trpc.deleteManual.useMutation({
    onSuccess: () => manualsQuery.refetch(),
  })

  const [file, setFile] = useState<File | null>(null)

  const upload = async () => {
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    await fetch(`${baseURL}/manuals`, { method: 'POST', body: form })
    setFile(null)
    manualsQuery.refetch()
  }

  return (
    <div className="container">
      <h1>Files to Training Security Chatbot</h1>
      <div>
        <input type="file" accept="application/pdf" onChange={e => setFile(e.target.files?.[0] ?? null)} />
        <button onClick={upload}>Add manual</button>
      </div>
      <ul>
        {manualsQuery.data?.map(m => (
          <li key={m} className="manual-item">
            <span className="pdf-icon">📄</span> {m}
            <button onClick={() => deleteManual.mutate({ filename: m })}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
