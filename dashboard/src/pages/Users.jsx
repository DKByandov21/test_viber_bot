import { useEffect, useState } from "react"
import { api } from "../api"
import { useAuth } from "../auth/AuthContext"

export default function Users() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    api.listUsers()
      .then((data) => {
        setUsers(data)
        setError(null)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleRoleChange = async (id, role) => {
    try {
      await api.updateUserRole(id, role)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  const handleDelete = async (id, email) => {
    if (!confirm(`Изтрий потребител "${email}"?`)) return
    try {
      await api.deleteUser(id)
      load()
    } catch (e) {
      setError(e.message)
    }
  }

  if (loading) return <p className="page-loading">Зареждане...</p>

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Потребители</h2>
        <span className="badge">{users.length}</span>
      </div>

      {error && <p className="error">Грешка: {error}</p>}

      <table>
        <thead>
          <tr>
            <th>Имейл</th>
            <th>Телефон</th>
            <th>Роля</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.email}</td>
              <td>{u.phone}</td>
              <td>
                <select value={u.role} onChange={(e) => handleRoleChange(u.id, e.target.value)} disabled={u.id === currentUser.id}>
                  <option value="admin">Admin</option>
                  <option value="agent">Agent</option>
                </select>
              </td>
              <td>
                {u.id !== currentUser.id && (
                  <button className="danger" onClick={() => handleDelete(u.id, u.email)}>Изтрий</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
