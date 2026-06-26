import { useEffect, useState } from "react"
import { projectsApi } from "../api"
import { STATUS_LABELS, TASK_STATUSES } from "../utils/tasks"

export default function Triage() {
  const [tasks, setTasks] = useState([])
  const [projects, setProjects] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [title, setTitle] = useState("")
  const [assign, setAssign] = useState({})

  const load = () => {
    Promise.all([projectsApi.triage(), projectsApi.list()])
      .then(([tasksData, projectsData]) => {
        setTasks(tasksData)
        setProjects(projectsData)
        setError(null)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!title.trim()) return
    try {
      await projectsApi.createTask({ title, status: "triage" })
      setTitle("")
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleAssign = async (taskId) => {
    const choice = assign[taskId]
    if (!choice) return
    try {
      await projectsApi.updateTask(taskId, { project_id: parseInt(choice, 10), status: "backlog" })
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDismiss = async (taskId, status) => {
    await projectsApi.updateTask(taskId, { status })
    load()
  }

  if (loading) return <p className="page-loading">Зареждане...</p>

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Triage</h2>
        <span className="badge">{tasks.length}</span>
      </div>

      {error && <p className="error">Грешка: {error}</p>}

      {tasks.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🛎️</div>
          <p>Няма нищо за triage в момента.</p>
        </div>
      ) : (
        tasks.map((t) => (
          <div key={t.id} className="agent-card">
            <h3>{t.title}</h3>
            {t.description && <p className="muted">{t.description}</p>}
            <div className="actions">
              <select value={assign[t.id] || ""} onChange={(e) => setAssign({ ...assign, [t.id]: e.target.value })}>
                <option value="">-- избери проект --</option>
                {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
              <button onClick={() => handleAssign(t.id)}>Прехвърли в проект</button>
              <select onChange={(e) => handleDismiss(t.id, e.target.value)} defaultValue="">
                <option value="" disabled>Друго действие...</option>
                {TASK_STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
              </select>
            </div>
          </div>
        ))
      )}

      <div className="settings-card">
        <h3>Нов triage запис</h3>
        <form onSubmit={handleCreate} className="form">
          <input placeholder="Кратко описание на проблема/задачата" value={title} onChange={(e) => setTitle(e.target.value)} required />
          <button type="submit">Добави</button>
        </form>
      </div>
    </div>
  )
}
