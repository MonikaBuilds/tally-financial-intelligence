import { useEffect, useRef, useState } from 'react'
import PageHeader from '../components/layout/PageHeader'
import { apiPost } from '../api/client'

const SUGGESTIONS = [
  'What is my revenue this month?',
  'Whom do I need to pay?',
  'Which invoices are pending?',
  'What are my outstanding receivables and payables?',
]

function Chatbot() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Hi! How can I assist you today? Ask me about your Profit & Loss, " +
        'receivables, payables, pending invoices, or any other report — ' +
        "I'll pull the numbers straight from Tally.",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function sendMessage(text) {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    setMessages((prev) => [...prev, { role: 'user', content: trimmed }])
    setInput('')
    setError(null)
    setLoading(true)

    try {
      const response = await apiPost('/chat', { message: trimmed })

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer,
          intent: response.intent,
          blocked: response.intent === 'write_operation',
        },
      ])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit(e) {
    e.preventDefault()
    sendMessage(input)
  }

  return (
    <>
      <PageHeader
        title="AI Financial Assistant"
        subtitle="Ask about your Tally data in plain language"
      />

      <div className="chat-card">
        <div className="chat-messages">
          {messages.map((m, i) => (
            <div
              key={i}
              className={
                m.role === 'user'
                  ? 'chat-bubble chat-bubble--user'
                  : m.blocked
                  ? 'chat-bubble chat-bubble--assistant chat-bubble--blocked'
                  : 'chat-bubble chat-bubble--assistant'
              }
            >
              {m.content}
            </div>
          ))}

          {loading && (
            <div className="chat-bubble chat-bubble--assistant chat-bubble--typing">
              Thinking…
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <div ref={bottomRef} />
        </div>

        {messages.length <= 1 && (
          <div className="chat-suggestions">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                type="button"
                className="chat-suggestion"
                onClick={() => sendMessage(s)}
                disabled={loading}
              >
                {s}
              </button>
            ))}
          </div>
        )}

        <form className="chat-input-row" onSubmit={handleSubmit}>
          <input
            className="chat-input"
            type="text"
            placeholder="Ask about revenue, payables, invoices…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button className="btn" type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </>
  )
}

export default Chatbot