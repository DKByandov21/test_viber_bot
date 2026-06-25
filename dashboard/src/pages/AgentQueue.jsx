import { useEffect, useState } from "react"
import { api } from "../api"

export default function AgentQueue() {
  const [queue, setQueue] = useState([])
  const [error, setError] = useState(null)
  const [replyText, setReplyText] = useState({})
  const [sending, setSending] = useState(null)

  const load = () => {
    api.agentQueue().then(setQueue).catch((e) => setError(e.message))
  }

  useEffect(load, [])

  const handleReply = async (sender, release) => {
    setSending(sender)
    try {
      await api.agentReply({ to: sender, text: replyText[sender] || "", release_agent_mode: release })
      setReplyText((prev) => ({ ...prev, [sender]: "" }))
      load()
    } catch (e) {
      setError(e.message)
    } finally {
      setSending(null)
    }
  }

  if (error) return <p className="error">Грешка: {error}</p>

  return (
    <div>
      <h2>Чакащи агент</h2>
      {queue.length === 0 && <p>Никой не чака агент в момента.</p>}
      {queue.map((c) => (
        <div key={c.sender} className="agent-card">
          <h3>{c.sender}</h3>
          <div className="chat-log small">
            {(c.history || []).slice(-4).map((msg, i) => (
              <div key={i} className={`bubble ${msg.role}`}>
                <strong>{msg.role}</strong>
                <p>{msg.content}</p>
              </div>
            ))}
          </div>
          <textarea
            value={replyText[c.sender] || ""}
            onChange={(e) => setReplyText((prev) => ({ ...prev, [c.sender]: e.target.value }))}
            placeholder="Отговор до клиента..."
          />
          <div className="actions">
            <button disabled={sending === c.sender} onClick={() => handleReply(c.sender, false)}>
              Изпрати
            </button>
            <button disabled={sending === c.sender} onClick={() => handleReply(c.sender, true)}>
              Изпрати и върни на AI
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
