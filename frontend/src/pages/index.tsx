import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { trpc } from '../utils/trpc'

export default function Home() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<{
    user: string
    bot: string
    url?: string | null
  }[]>([])
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)

  const mutation = trpc.sendMessage.useMutation({
    onSuccess(data) {
      setMessages(prev => [
        ...prev,
        { user: input, bot: data.response, url: data.url },
      ])
      if (data.url) {
        setPdfUrl(data.url.replace('./', 'http://localhost:8000/'))
      }
      setInput('')
    },
  })

  return (
    <div className="container">
      <h1>MTG Security Chatbot</h1>
      <a href="/config">Configuración</a>
      <div className="layout">
        <div className="chat-area">
          <div className="chat-box">
            {messages.map((m, i) => (
              <div key={i} className="message">
                <div className="user"><strong>Usuario:</strong> {m.user}</div>
                <div className="bot">
                  <strong>Bot:</strong>{' '}
                  <ReactMarkdown>{m.bot}</ReactMarkdown>
                </div>
              </div>
            ))}
          </div>
        </div>
        {pdfUrl && (
          <iframe className="pdf-viewer" src={pdfUrl} title="Manual" />
        )}
      </div>
      <form
        onSubmit={e => {
          e.preventDefault()
          mutation.mutate({ message: input })
        }}
        className="input-form"
      >
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Escribe tu mensaje"
        />
        <button type="submit">Enviar</button>
      </form>
    </div>
  )
}
