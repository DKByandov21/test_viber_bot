import { useEffect, useState } from "react"
import { api } from "../api"

const EMPTY_FORM = { key: "", id: "", language: "bg", params: "", description: "" }

export default function Templates() {
  const [templates, setTemplates] = useState([])
  const [error, setError] = useState(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [editingKey, setEditingKey] = useState(null)

  const load = () => {
    api.listTemplates().then(setTemplates).catch((e) => setError(e.message))
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
    if (!confirm(`Изтрий template "${key}"?`)) return
    await api.deleteTemplate(key)
    load()
  }

  if (error) return <p className="error">Грешка: {error}</p>

  return (
    <div>
      <h2>Templates</h2>
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
                <button onClick={() => startEdit(t)}>Редактирай</button>
                <button onClick={() => handleDelete(t.key)}>Изтрий</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

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
          {editingKey && <button type="button" onClick={resetForm}>Отказ</button>}
        </div>
      </form>
    </div>
  )
}
