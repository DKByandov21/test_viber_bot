import { useEffect, useState } from "react"
import { api } from "../api"

export default function Notify() {
  const [templates, setTemplates] = useState([])
  const [to, setTo] = useState("")
  const [templateKey, setTemplateKey] = useState("")
  const [placeholders, setPlaceholders] = useState({})
  const [contextSummary, setContextSummary] = useState("")
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.listTemplates().then(setTemplates).catch((e) => setError(e.message))
  }, [])

  const selected = templates.find((t) => t.key === templateKey)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    try {
      const res = await api.notify({
        to,
        template: templateKey,
        placeholders,
        context_summary: contextSummary || undefined,
      })
      setResult(res)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div>
      <h2>Изпрати Notify</h2>
      <form onSubmit={handleSubmit} className="form">
        <input placeholder="Телефон (напр. 359...)" value={to} onChange={(e) => setTo(e.target.value)} required />

        <select value={templateKey} onChange={(e) => { setTemplateKey(e.target.value); setPlaceholders({}) }} required>
          <option value="">-- избери template --</option>
          {templates.map((t) => (
            <option key={t.key} value={t.key}>{t.key}</option>
          ))}
        </select>

        {selected && (selected.params || []).map((p) => (
          <input
            key={p}
            placeholder={`Параметър: ${p}`}
            value={placeholders[p] || ""}
            onChange={(e) => setPlaceholders({ ...placeholders, [p]: e.target.value })}
          />
        ))}

        <textarea
          placeholder="Контекст за паметта на разговора (по желание)"
          value={contextSummary}
          onChange={(e) => setContextSummary(e.target.value)}
        />

        <button type="submit">Изпрати</button>
      </form>

      {error && <p className="error">Грешка: {error}</p>}
      {result && <pre className="result">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
