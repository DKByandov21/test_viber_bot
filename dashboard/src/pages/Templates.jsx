import { useEffect, useState } from "react"
import { api } from "../api"

const EMPTY_FORM = { key: "", id: "", language: "bg", params: "", description: "" }

export default function Templates() {
  const [templates, setTemplates] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(EMPTY_FORM)
  const [editingKey, setEditingKey] = useState(null)
  const [deletingKey, setDeletingKey] = useState(null)

  const load = () => {
    api.listTemplates()
      .then((data) => {
        setTemplates(data)
        setError(null)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const startEdit = (t) => {
    setEditingKey(t.key)
    setForm({ key: t.key, id: t.id, language: t.language, params: (t.params || []).join(","), description: t.description || "" })
  }

  const resetForm = () => {
    setEditingKey(null)
    setForm(EMPTY_FORM)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    const payload = {
      key: form.key,
      id: form.id,
      language: form.language,
      params: form.params.split(",").map((p) => p.trim()).filter(Boolean),
      description: form.description,
    }
    try {
      if (editingKey) {
        await api.updateTemplate(editingKey, payload)
      } else {
        await api.createTemplate(payload)
      }
      resetForm()
      load()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (key) => {
    if (!confirm(`Изтрий template "${key}"? Това действие е окончателно.`)) return
    setDeletingKey(key)
    setError(null)
    try {
      await api.deleteTemplate(key)
      load()
    } catch (err) {
      setError(err.message)
    } finally {
      setDeletingKey(null)
    }
  }

  if (loading) return <p className="page-loading">Зареждане...</p>

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Templates</h2>
        <span className="badge">{templates.length}</span>
      </div>

      {error && <p className="error">Грешка: {error}</p>}

      {templates.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <p>Няма templates все още.</p>
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Key</th>
              <th>Template ID</th>
              <th>Language</th>
              <th>Params</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {templates.map((t) => (
              <tr key={t.key}>
                <td>{t.key}</td>
                <td className="mono">{t.id}</td>
                <td>{t.language}</td>
                <td>{(t.params || []).join(", ")}</td>
                <td>
                  <div className="actions">
                    <button className="secondary" onClick={() => startEdit(t)}>Редактирай</button>
                    <button className="danger" disabled={deletingKey === t.key} onClick={() => handleDelete(t.key)}>
                      {deletingKey === t.key ? "Изтрива се..." : "Изтрий"}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="settings-card">
        <h3>{editingKey ? `Редактирай "${editingKey}"` : "Нов template"}</h3>
        <form onSubmit={handleSubmit} className="form">
          <input
            placeholder="key (напр. order_confirmation)"
            value={form.key}
            disabled={!!editingKey}
            onChange={(e) => setForm({ ...form, key: e.target.value })}
            required
          />
          <input
            placeholder="Infobip template ID"
            value={form.id}
            onChange={(e) => setForm({ ...form, id: e.target.value })}
            required
          />
          <input
            placeholder="language (bg/en)"
            value={form.language}
            onChange={(e) => setForm({ ...form, language: e.target.value })}
          />
          <input
            placeholder="params, comma separated (1,2,3 или pin)"
            value={form.params}
            onChange={(e) => setForm({ ...form, params: e.target.value })}
          />
          <input
            placeholder="description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <div className="actions">
            <button type="submit">{editingKey ? "Запази" : "Добави"}</button>
            {editingKey && <button type="button" className="secondary" onClick={resetForm}>Отказ</button>}
          </div>
        </form>
      </div>
    </div>
  )
}
