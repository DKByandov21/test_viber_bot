import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../api"
import { formatTime, withSessionBreaks } from "../utils/time"
import { roleLabel } from "../utils/roles"

export default function ConversationDetail() {
  const { sender } = useParams()
  const [history, setHistory] = useState([])
  const [sessions, setSessions] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    Promise.all([api.getConversation(sender), api.listSessions(sender)])
      .then(([convo, pastSessions]) => {
        setHistory(convo.history || [])
        setSessions(pastSessions)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [sender])

  const handleReset = async () => {
    await api.resetConversation(sender)
    load()
  }

  if (loading) return <p className="page-loading">Зареждане...</p>
  if (error) return <p className="error">Грешка: {error}</p>

  const items = withSessionBreaks(history)

  return (
    <div className="fade-in">
      <Link to="/" className="back-link">← Всички разговори</Link>
      <div className="page-header">
        <h2>{sender}</h2>
        <button className="secondary" onClick={handleReset}>Приключи текущата сесия</button>
      </div>

      <h3>Текуща сесия</h3>
      <div className="chat-log">
        {history.length === 0 && <p className="muted">Няма съобщения в текущата сесия.</p>}
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

      {sessions.length > 0 && (
        <>
          <h3>Минали сесии ({sessions.length})</h3>
          <table>
            <thead>
              <tr>
                <th>Започната</th>
                <th>Приключена</th>
                <th>Съобщения</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr key={s.id}>
                  <td>{formatTime(s.started_at)}</td>
                  <td>{formatTime(s.ended_at)}</td>
                  <td>{(s.history || []).length}</td>
                  <td>
                    <Link to={`/conversations/${encodeURIComponent(sender)}/sessions/${s.id}`}>Виж →</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  )
}
