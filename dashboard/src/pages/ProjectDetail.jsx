import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { projectsApi } from "../api"
import { PRIORITIES, PRIORITY_LABELS, STATUS_LABELS, TASK_STATUSES } from "../utils/tasks"

function Board({ projectId }) {
  const [tasks, setTasks] = useState([])
  const [error, setError] = useState(null)
  const [title, setTitle] = useState("")

  const load = () => {
    projectsApi.listTasks({ project_id: projectId }).then(setTasks).catch((e) => setError(e.message))
  }

  useEffect(load, [projectId])

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!title.trim()) return
    try {
      await projectsApi.createTask({ title, project_id: projectId, status: "backlog" })
      setTitle("")
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleStatusChange = async (taskId, status) => {
    await projectsApi.updateTask(taskId, { status })
    load()
  }

  const handlePriorityChange = async (taskId, priority) => {
    await projectsApi.updateTask(taskId, { priority })
    load()
  }

  const handleDelete = async (taskId) => {
    if (!confirm("Изтрий задачата?")) return
    await projectsApi.removeTask(taskId)
    load()
  }

  if (error) return <p className="error">Грешка: {error}</p>

  return (
    <div>
      <form onSubmit={handleCreate} className="form inline-form">
        <input placeholder="Нова задача..." value={title} onChange={(e) => setTitle(e.target.value)} />
        <button type="submit">Добави</button>
      </form>

      <div className="kanban">
        {TASK_STATUSES.map((status) => (
          <div key={status} className="kanban-column">
            <h4>{STATUS_LABELS[status]} <span className="muted">({tasks.filter((t) => t.status === status).length})</span></h4>
            {tasks.filter((t) => t.status === status).map((t) => (
              <div key={t.id} className="task-card">
                <p>{t.title}</p>
                <div className="task-card-controls">
                  <select value={t.status} onChange={(e) => handleStatusChange(t.id, e.target.value)}>
                    {TASK_STATUSES.map((s) => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
                  </select>
                  <select value={t.priority} onChange={(e) => handlePriorityChange(t.id, e.target.value)}>
                    {PRIORITIES.map((p) => <option key={p} value={p}>{PRIORITY_LABELS[p]}</option>)}
                  </select>
                </div>
                <button className="danger small" onClick={() => handleDelete(t.id)}>Изтрий</button>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

function Sprints({ projectId }) {
  const [sprints, setSprints] = useState([])
  const [error, setError] = useState(null)
  const [name, setName] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")

  const load = () => {
    projectsApi.listSprints(projectId).then(setSprints).catch((e) => setError(e.message))
  }

  useEffect(load, [projectId])

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      await projectsApi.createSprint(projectId, { name, start_date: startDate || null, end_date: endDate || null })
      setName("")
      setStartDate("")
      setEndDate("")
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleStatusChange = async (id, status) => {
    await projectsApi.updateSprint(id, { status })
    load()
  }

  const handleDelete = async (id) => {
    if (!confirm("Изтрий спринта?")) return
    await projectsApi.removeSprint(id)
    load()
  }

  if (error) return <p className="error">Грешка: {error}</p>

  return (
    <div>
      <table>
        <thead>
          <tr><th>Име</th><th>Начало</th><th>Край</th><th>Статус</th><th></th></tr>
        </thead>
        <tbody>
          {sprints.map((s) => (
            <tr key={s.id}>
              <td>{s.name}</td>
              <td>{s.start_date || "-"}</td>
              <td>{s.end_date || "-"}</td>
              <td>
                <select value={s.status} onChange={(e) => handleStatusChange(s.id, e.target.value)}>
                  <option value="planned">Planned</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                </select>
              </td>
              <td><button className="danger" onClick={() => handleDelete(s.id)}>Изтрий</button></td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="settings-card">
        <h3>Нов sprint</h3>
        <form onSubmit={handleCreate} className="form">
          <input placeholder="Име" value={name} onChange={(e) => setName(e.target.value)} required />
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          <button type="submit">Създай</button>
        </form>
      </div>
    </div>
  )
}

function Docs({ projectId }) {
  const [docs, setDocs] = useState([])
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const [title, setTitle] = useState("")
  const [content, setContent] = useState("")

  const load = () => {
    projectsApi.listDocs(projectId).then(setDocs).catch((e) => setError(e.message))
  }

  useEffect(load, [projectId])

  const startNew = () => {
    setSelected("new")
    setTitle("")
    setContent("")
  }

  const openDoc = (doc) => {
    setSelected(doc.id)
    setTitle(doc.title)
    setContent(doc.content)
  }

  const handleSave = async (e) => {
    e.preventDefault()
    try {
      if (selected === "new") {
        await projectsApi.createDoc(projectId, { title, content })
      } else {
        await projectsApi.updateDoc(selected, { title, content })
      }
      setSelected(null)
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm("Изтрий документа?")) return
    await projectsApi.removeDoc(id)
    setSelected(null)
    load()
  }

  if (error) return <p className="error">Грешка: {error}</p>

  if (selected !== null) {
    return (
      <div>
        <form onSubmit={handleSave} className="form">
          <input placeholder="Заглавие" value={title} onChange={(e) => setTitle(e.target.value)} required />
          <textarea
            placeholder="Markdown съдържание..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="doc-editor"
          />
          <div className="actions">
            <button type="submit">Запази</button>
            <button type="button" className="secondary" onClick={() => setSelected(null)}>Отказ</button>
            {selected !== "new" && <button type="button" className="danger" onClick={() => handleDelete(selected)}>Изтрий</button>}
          </div>
        </form>
      </div>
    )
  }

  return (
    <div>
      <button onClick={startNew}>+ Нов документ</button>
      <div className="docs-list">
        {docs.map((d) => (
          <div key={d.id} className="doc-card" onClick={() => openDoc(d)}>
            <h4>{d.title}</h4>
            <p className="muted">{(d.content || "").slice(0, 120)}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function ProjectDetail() {
  const { id } = useParams()
  const projectId = parseInt(id, 10)
  const [project, setProject] = useState(null)
  const [error, setError] = useState(null)
  const [tab, setTab] = useState("board")

  useEffect(() => {
    projectsApi.get(projectId).then(setProject).catch((e) => setError(e.message))
  }, [projectId])

  if (error) return <p className="error">Грешка: {error}</p>
  if (!project) return <p className="page-loading">Зареждане...</p>

  return (
    <div className="fade-in">
      <Link to="/projects" className="back-link">← Всички проекти</Link>
      <div className="page-header">
        <h2>{project.name}</h2>
      </div>
      {project.description && <p className="muted">{project.description}</p>}

      <div className="tabs">
        {["board", "sprints", "docs"].map((t) => (
          <button key={t} className={tab === t ? "tab active" : "tab"} onClick={() => setTab(t)}>
            {t === "board" ? "Board" : t === "sprints" ? "Sprints" : "Docs"}
          </button>
        ))}
      </div>

      {tab === "board" && <Board projectId={projectId} />}
      {tab === "sprints" && <Sprints projectId={projectId} />}
      {tab === "docs" && <Docs projectId={projectId} />}
    </div>
  )
}
