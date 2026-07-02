import { useEffect, useState } from "react"
import { knowledgeApi } from "../api"

const EMPTY = { title: "", content: "" }

export default function Knowledge() {
  const [entries, setEntries] = useState([])
  const [fileChunks, setFileChunks] = useState(0)
  const [editing, setEditing] = useState(null) // null | { id?, title, content }
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState("")

  const load = () => {
    setLoading(true)
    knowledgeApi.list()
      .then((data) => {
        setEntries(data.entries)
        setFileChunks(data.file_chunks)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSave = async () => {
    if (!editing?.title?.trim() || !editing?.content?.trim()) return
    setSaving(true)
    setError(null)
    try {
      if (editing.id) {
        const updated = await knowledgeApi.update(editing.id, { title: editing.title, content: editing.content })
        setEntries((prev) => prev.map((e) => e.id === editing.id ? updated : e))
      } else {
        const created = await knowledgeApi.create({ title: editing.title, content: editing.content })
        setEntries((prev) => [created, ...prev])
      }
      setEditing(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm("Изтриване на записа?")) return
    await knowledgeApi.remove(id)
    setEntries((prev) => prev.filter((e) => e.id !== id))
    if (editing?.id === id) setEditing(null)
  }

  const filtered = entries.filter(
    (e) => !search || e.title.toLowerCase().includes(search.toLowerCase()) || e.content.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Knowledge Base</h2>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <span className="badge muted" title="Статични .md файлове в /docs">
            📄 {fileChunks} файлови chunk-а
          </span>
          <span className="badge" title="Записи в базата данни">
            🗃️ {entries.length} DB записа
          </span>
          <button onClick={() => setEditing(EMPTY)}>+ Нов запис</button>
        </div>
      </div>

      <p className="muted" style={{ marginBottom: 16, fontSize: 13 }}>
        Записите тук се включват в RAG контекста на AI бота — при въпрос, AI-то търси в тях лексикално и ги цитира.
      </p>

      {error && <p className="error">{error}</p>}

      {editing && (
        <div className="settings-card" style={{ marginBottom: 24 }}>
          <h3>{editing.id ? "Редактиране" : "Нов запис"}</h3>
          <div className="form">
            <label>Заглавие</label>
            <input
              value={editing.title}
              onChange={(e) => setEditing((ed) => ({ ...ed, title: e.target.value }))}
              placeholder="Кратко описание / тема"
              autoFocus
            />
            <label>Съдържание</label>
            <textarea
              value={editing.content}
              onChange={(e) => setEditing((ed) => ({ ...ed, content: e.target.value }))}
              rows={10}
              placeholder={"Наш продукт X прави Y...\n\nЧесто задавани въпроси:\n- ..."}
              style={{ fontFamily: "monospace", fontSize: 13 }}
            />
            <span className="muted" style={{ fontSize: 12 }}>{editing.content.length} символа</span>
            <div style={{ display: "flex", gap: 8 }}>
              <button onClick={handleSave} disabled={saving || !editing.title.trim() || !editing.content.trim()}>
                {saving ? "Запазване..." : "Запази"}
              </button>
              <button className="secondary" onClick={() => setEditing(null)}>Отказ</button>
            </div>
          </div>
        </div>
      )}

      <input
        placeholder="Търси в записите..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ marginBottom: 16, maxWidth: 360 }}
      />

      {loading ? (
        <p className="muted">Зарежда...</p>
      ) : filtered.length === 0 ? (
        <p className="muted">{search ? "Няма резултати." : "Няма записи. Добави първия с бутона горе."}</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {filtered.map((e) => (
            <div key={e.id} className="settings-card" style={{ padding: "12px 16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <strong style={{ fontSize: 15 }}>{e.title}</strong>
                  <p className="muted" style={{ margin: "4px 0 0", fontSize: 13, whiteSpace: "pre-wrap", maxHeight: 80, overflow: "hidden" }}>
                    {e.content}
                  </p>
                </div>
                <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                  <button className="secondary" style={{ fontSize: 12, padding: "3px 10px" }} onClick={() => setEditing(e)}>
                    Редактирай
                  </button>
                  <button
                    className="secondary"
                    style={{ fontSize: 12, padding: "3px 10px", color: "var(--danger)" }}
                    onClick={() => handleDelete(e.id)}
                  >
                    Изтрий
                  </button>
                </div>
              </div>
              {e.updated_at && (
                <p className="muted" style={{ fontSize: 11, marginTop: 6 }}>
                  Обновен: {new Date(e.updated_at).toLocaleString("bg-BG")}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
