import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../api"
import { formatTime } from "../utils/time"
import { roleLabel } from "../utils/roles"

export default function SessionDetail() {
  const { sender, id } = useParams()
  const [session, setSession] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getSession(id)
      .then(setSession)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <p className="page-loading">Зареждане...</p>
  if (error) return <p className="error">Грешка: {error}</p>

  return (
    <div className="fade-in">
      <Link to={`/conversations/${encodeURIComponent(sender)}`} className="back-link">← Назад към {sender}</Link>
      <div className="page-header">
        <h2>Сесия от {formatTime(session.started_at)}</h2>
      </div>
      <p className="muted">Приключила: {formatTime(session.ended_at)}</p>
      <div className="chat-log">
        {(session.history || []).map((msg, i) => (
          <div key={i} className={`bubble ${msg.role}`}>
            <strong>{roleLabel(msg.role)}</strong>
            <p>{msg.content}</p>
            {msg.at && <span className="bubble-time">{formatTime(msg.at)}</span>}
          </div>
        ))}
      </div>
    </div>
  )
}
