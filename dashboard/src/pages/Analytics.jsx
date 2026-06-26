import { useEffect, useState } from "react"
import { api } from "../api"

const CARDS = [
  { key: "total_customers", label: "Уникални клиенти", accent: "" },
  { key: "total_sessions", label: "Общо сесии", accent: "accent" },
  { key: "total_messages", label: "Общо съобщения", accent: "" },
  { key: "messages_today", label: "Съобщения днес", accent: "accent" },
  { key: "active_now", label: "Активни сега", accent: "accent" },
  { key: "agent_queue_count", label: "Чакат агент", accent: "warn" },
  { key: "agent_handled_sessions", label: "Обработени от агент", accent: "" },
  { key: "ai_only_sessions", label: "Само AI", accent: "" },
]

export default function Analytics() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.stats()
      .then(setStats)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="page-loading">Зареждане...</p>
  if (error) return <p className="error">Грешка: {error}</p>

  return (
    <div className="fade-in">
      <h2>Analytics</h2>
      <div className="stats-grid">
        {CARDS.map((c) => (
          <div key={c.key} className={`stat-card ${c.accent}`}>
            <div className="stat-value">{stats[c.key]}</div>
            <div className="stat-label">{c.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
