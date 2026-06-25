import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "../api"

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

  if (loading) return <p>Зареждане...</p>
  if (error) return <p className="error">Грешка: {error}</p>

  return (
    <div>
      <h2>Разговори</h2>
      {conversations.length === 0 && <p>Няма разговори все още.</p>}
      <table>
        <thead>
          <tr>
            <th>Sender</th>
            <th>Agent Mode</th>
            <th>Последна активност</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {conversations.map((c) => (
            <tr key={c.sender}>
              <td>{c.sender}</td>
              <td>{c.agent_mode ? "Да" : "Не"}</td>
              <td>{c.updated_at}</td>
              <td>
                <Link to={`/conversations/${encodeURIComponent(c.sender)}`}>Виж</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
