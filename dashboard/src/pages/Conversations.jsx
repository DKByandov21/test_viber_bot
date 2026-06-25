import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "../api"
import { timeAgo } from "../utils/time"

export default function Conversations() {
  const [conversations, setConversations] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.listConversations()
      .then(setConversations)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="page-loading">Зареждане...</p>
  if (error) return <p className="error">Грешка: {error}</p>

  const activeCount = conversations.filter((c) => c.is_active).length
  const agentCount = conversations.filter((c) => c.agent_mode).length

  return (
    <div className="fade-in">
      <h2>Разговори</h2>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-value">{conversations.length}</div>
          <div className="stat-label">Общо разговори</div>
        </div>
        <div className="stat-card accent">
          <div className="stat-value">{activeCount}</div>
          <div className="stat-label">Активни сега</div>
        </div>
        <div className="stat-card warn">
          <div className="stat-value">{agentCount}</div>
          <div className="stat-label">Чакат агент</div>
        </div>
      </div>

      {conversations.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">💬</div>
          <p>Няма разговори все още.</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Sender</th>
              <th>Статус</th>
              <th>Последна активност</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {conversations.map((c) => (
              <tr key={c.sender}>
                <td>{c.sender}</td>
                <td>
                  {c.agent_mode ? (
                    <span className="status-pill agent">Agent</span>
                  ) : c.is_active ? (
                    <span className="status-pill active">● Active</span>
                  ) : (
                    <span className="status-pill closed">Closed</span>
                  )}
                </td>
                <td className="muted">{timeAgo(c.updated_at)}</td>
                <td>
                  <Link to={`/conversations/${encodeURIComponent(c.sender)}`}>Виж →</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
