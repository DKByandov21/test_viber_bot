import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import { api } from "../api"

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

  if (loading) return <p>Зареждане...</p>
  if (error) return <p className="error">Грешка: {error}</p>

  return (
    <div>
      <h2>Разговор с {sender}</h2>
      <button onClick={handleReset}>Изчисти разговора</button>
      <div className="chat-log">
        {history.length === 0 && <p>Няма съобщения.</p>}
        {history.map((msg, i) => (
          <div key={i} className={`bubble ${msg.role}`}>
            <strong>{msg.role}</strong>
            <p>{msg.content}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
