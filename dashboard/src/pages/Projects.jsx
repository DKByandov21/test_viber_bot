import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { projectsApi } from "../api"

export default function Projects() {
  const [projects, setProjects] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")

  const load = () => {
    projectsApi.list()
      .then((data) => {
        setProjects(data)
        setError(null)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      await projectsApi.create({ name, description })
      setName("")
      setDescription("")
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <p className="page-loading">Зареждане...</p>

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Проекти</h2>
        <span className="badge">{projects.length}</span>
      </div>

      {error && <p className="error">Грешка: {error}</p>}

      {projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📁</div>
          <p>Няма проекти все още.</p>
        </div>
      ) : (
        <div className="project-grid">
          {projects.map((p) => (
            <Link key={p.id} to={`/projects/${p.id}`} className="project-card">
              <h3>{p.name}</h3>
              <p className="muted">{p.description || "Без описание"}</p>
            </Link>
          ))}
        </div>
      )}

      <div className="settings-card">
        <h3>Нов проект</h3>
        <form onSubmit={handleCreate} className="form">
          <input placeholder="Име на проекта" value={name} onChange={(e) => setName(e.target.value)} required />
          <textarea placeholder="Описание (по желание)" value={description} onChange={(e) => setDescription(e.target.value)} />
          <button type="submit">Създай</button>
        </form>
      </div>
    </div>
  )
}
