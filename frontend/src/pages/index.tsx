import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export default function Home() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<{
    user: string
    bot: string
    url?: string | null
  }[]>([])
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const chatBoxRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const box = chatBoxRef.current
    if (box) {
      box.scrollTop = box.scrollHeight
    }
  }, [messages])

  const sendMessage = async () => {
    const res = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input }),
    })
    const data = await res.json()
    setMessages(prev => [
      ...prev,
      { user: input, bot: data.response, url: data.url },
    ])
    if (data.url) {
      setPdfUrl(data.url.replace('./', 'http://localhost:8000/'))
    }
    setInput('')
  }

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
              sendMessage()
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
