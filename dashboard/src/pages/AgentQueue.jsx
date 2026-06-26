import { useEffect, useRef, useState } from "react"
import { api } from "../api"
import { timeAgo, withSessionBreaks } from "../utils/time"
import { roleLabel } from "../utils/roles"

const POLL_INTERVAL_MS = 8000

function AgentCard({ conversation, replyValue, sending, onChangeReply, onReply }) {
  const logRef = useRef(null)

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [conversation.history])

  return (
    <div className="agent-card">
      <div className="agent-card-header">
        <h3>{conversation.sender}</h3>
        <span className="muted">{timeAgo(conversation.updated_at)}</span>
      </div>
      <div className="chat-log scrollable" ref={logRef}>
        {withSessionBreaks(conversation.history || []).map((item, i) =>
          item.separator ? (
            <div key={item.key} className="session-separator">Нова сесия</div>
          ) : (
            <div key={i} className={`bubble ${item.role}`}>
              <strong>{roleLabel(item.role)}</strong>
              <p>{item.content}</p>
              {item.at && <span className="bubble-time">{timeAgo(item.at)}</span>}
            </div>
          )
        )}
      </div>
      <textarea
        value={replyValue || ""}
        onChange={(e) => onChangeReply(e.target.value)}
        placeholder="Отговор до клиента..."
      />
      <div className="actions">
        <button disabled={sending} onClick={() => onReply(false)}>
          Изпрати
        </button>
        <button className="secondary" disabled={sending} onClick={() => onReply(true)}>
          Изпрати и върни на AI
        </button>
      </div>
    </div>
  )
}

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
    <div className="fade-in">
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
        <AgentCard
          key={c.sender}
          conversation={c}
          replyValue={replyText[c.sender]}
          sending={sending === c.sender}
          onChangeReply={(value) => setReplyText((prev) => ({ ...prev, [c.sender]: value }))}
          onReply={(release) => handleReply(c.sender, release)}
        />
      ))}
    </div>
  )
}
