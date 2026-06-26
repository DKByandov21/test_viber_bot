import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../api"
import { formatTime, withSessionBreaks } from "../utils/time"
import { roleLabel } from "../utils/roles"

export default function ConversationDetail() {
  const { sender } = useParams()
  const [history, setHistory] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getConversation(sender)
      .then((data) => setHistory(data.history || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [sender])

  const handleReset = async () => {
    await api.resetConversation(sender)
    setHistory([])
  }

  if (loading) return <p className="page-loading">Зареждане...</p>
  if (error) return <p className="error">Грешка: {error}</p>

  const items = withSessionBreaks(history)

  return (
    <div className="fade-in">
      <Link to="/" className="back-link">← Всички разговори</Link>
      <div className="page-header">
        <h2>{sender}</h2>
        <button className="secondary" onClick={handleReset}>Изчисти разговора</button>
      </div>
      <div className="chat-log">
        {history.length === 0 && <p className="muted">Няма съобщения.</p>}
        {items.map((item, i) =>
          item.separator ? (
            <div key={item.key} className="session-separator">Нова сесия</div>
          ) : (
            <div key={i} className={`bubble ${item.role}`}>
              <strong>{roleLabel(item.role)}</strong>
              <p>{item.content}</p>
              {item.at && <span className="bubble-time">{formatTime(item.at)}</span>}
            </div>
          )
        )}
      </div>
    </div>
  )
}
