import { useState } from 'react'
import { trpc } from '../utils/trpc'

export default function Home() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<{ user: string; bot: string }[]>([])

  const mutation = trpc.sendMessage.useMutation({
    onSuccess(data) {
      setMessages(prev => [...prev, { user: input, bot: data.response }])
      setInput('')
    },
  })

  return (
    <div className="container">
      <h1>MTG Security Chatbot</h1>
      <div className="chat-box">
        {messages.map((m, i) => (
          <div key={i} className="message">
            <strong>Usuario:</strong> {m.user}
            <br />
            <strong>Bot:</strong> {m.bot}
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
