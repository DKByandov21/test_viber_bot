import { useEffect, useState } from "react"
import { api } from "../api"
import { timeAgo } from "../utils/time"

const POLL_INTERVAL_MS = 8000

export default function AgentQueue() {
  const [queue, setQueue] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [replyText, setReplyText] = useState({})
  const [sending, setSending] = useState(null)

  const load = () => {
    api.agentQueue()
      .then((data) => {
        setQueue(data)
        setError(null)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, POLL_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [])

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

  return (
    <div>
      <div className="page-header">
        <h2>Чакащи агент</h2>
        <span className="badge">{queue.length}</span>
      </div>

      {error && <p className="error">Грешка: {error}</p>}

      {!loading && queue.length === 0 && !error && (
        <div className="empty-state">
          <div className="empty-icon">✅</div>
          <p>Никой не чака агент в момента.</p>
          <p className="muted">Списъкът се обновява автоматично на всеки {POLL_INTERVAL_MS / 1000}с.</p>
        </div>
      )}

      {queue.map((c) => (
        <div key={c.sender} className="agent-card">
          <div className="agent-card-header">
            <h3>{c.sender}</h3>
            <span className="muted">{timeAgo(c.updated_at)}</span>
          </div>
          <div className="chat-log small">
            {(c.history || []).slice(-4).map((msg, i) => (
              <div key={i} className={`bubble ${msg.role}`}>
                <strong>{msg.role === "user" ? "Клиент" : "Бот"}</strong>
                <p>{msg.content}</p>
                {msg.at && <span className="bubble-time">{timeAgo(msg.at)}</span>}
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
            <button className="secondary" disabled={sending === c.sender} onClick={() => handleReply(c.sender, true)}>
              Изпрати и върни на AI
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
