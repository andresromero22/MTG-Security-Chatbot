import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { trpc } from '../utils/trpc'

const baseURL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export default function Home() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<{
    user: string
    bot: string
    url?: string | null
  }[]>([])
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const chatBoxRef = useRef<HTMLDivElement>(null)

  const handleClear = () => {
    setMessages([])
    setPdfUrl(null)
  }

  useEffect(() => {
    const box = chatBoxRef.current
    if (box) {
      box.scrollTop = box.scrollHeight
    }
  }, [messages])

  const mutation = trpc.sendMessage.useMutation({
    onSuccess(data) {
      setMessages(prev => {
        const newMsgs = [
          ...prev,
          { user: input, bot: data.response, url: data.url },
        ]
        return newMsgs.slice(-5)
      })
      if (data.url) {
        setPdfUrl(data.url.replace('./', `${baseURL}/`))
      }
      setInput('')
    },
  })

  return (
    <div className="container">
      <h1>MTG Security Chatbot</h1>
      <div className="layout">
        <div className="chat-area">
          <div className="chat-box" ref={chatBoxRef}>
            {messages.map((m, i) => (
              <div key={i} className="message">
                <div className="user"><strong>User:</strong> {m.user}</div>
                <div className="bot">
                  <strong>KalGuard:</strong>{' '}
                  <ReactMarkdown>
                    {(String(m.bot))}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
          </div>
          <form
            onSubmit={e => {
              e.preventDefault()
              mutation.mutate({ message: input })
            }}
            className="input-form"
            >
            {/* <div className='chat-area'> */}
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Escribe tu mensaje"
                />
              <button type="submit">Enviar</button>
              <button
                type="button"
                className="clear-button"
                onClick={handleClear}
                title="Limpiar historial"
              >
                🗑️
              </button>
            {/* </div> */}
          </form>
        </div>
        {pdfUrl && (
          <iframe className="pdf-viewer" src={pdfUrl} title="Manual" />
        )}
      </div>
    </div>
  )
}
