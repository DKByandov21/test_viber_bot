import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../api"
import { formatTime } from "../utils/time"

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

  return (
    <div className="fade-in">
      <Link to="/" className="back-link">← Всички разговори</Link>
      <div className="page-header">
        <h2>{sender}</h2>
        <button className="secondary" onClick={handleReset}>Изчисти разговора</button>
      </div>
      <div className="chat-log">
        {history.length === 0 && <p className="muted">Няма съобщения.</p>}
        {history.map((msg, i) => (
          <div key={i} className={`bubble ${msg.role}`}>
            <strong>{msg.role === "user" ? "Клиент" : "Бот"}</strong>
            <p>{msg.content}</p>
            {msg.at && <span className="bubble-time">{formatTime(msg.at)}</span>}
          </div>
        ))}
      </div>
    </div>
  )
}
