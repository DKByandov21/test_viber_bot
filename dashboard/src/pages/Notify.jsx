import { useEffect, useState } from "react"
import { api } from "../api"

const RAW_PLACEHOLDER = `{
  "sender": "tPlay",
  "destinations": [{"to": "359889303693", "messageId": "6568e6fc-8fd1-404d-8f36-5a70998090af"}],
  "content": {
    "type": "TEMPLATE",
    "templateId": "e17a5323-3114-4597-a949-17d4b80917d8",
    "language": "bg",
    "parameters": {"p1": "50100000001", "p2": "15.07.2026", "p3": "Александър Табаков"}
  },
  "options": {
    "validityPeriod": {"amount": 1800, "timeUnit": "SECONDS"},
    "smsFailover": {"sender": "1970", "text": "Tova e SMS"}
  }
}`

function TemplateForm() {
  const [templates, setTemplates] = useState([])
  const [to, setTo] = useState("")
  const [templateKey, setTemplateKey] = useState("")
  const [placeholders, setPlaceholders] = useState({})
  const [contextSummary, setContextSummary] = useState("")
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [sending, setSending] = useState(false)

  useEffect(() => {
    api.listTemplates().then(setTemplates).catch((e) => setError(e.message))
  }, [])

  const selected = templates.find((t) => t.key === templateKey)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    setSending(true)
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
    } finally {
      setSending(false)
    }
  }

  return (
    <>
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

        <button type="submit" disabled={sending}>{sending ? "Изпраща се..." : "Изпрати"}</button>
      </form>

      {error && <p className="error">Грешка: {error}</p>}
      {result && <pre className="result">{JSON.stringify(result, null, 2)}</pre>}
    </>
  )
}

function RawJsonForm() {
  const [raw, setRaw] = useState(RAW_PLACEHOLDER)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [sending, setSending] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)

    let message
    try {
      message = JSON.parse(raw)
    } catch {
      setError("Невалиден JSON")
      return
    }

    setSending(true)
    try {
      const res = await api.notifyRaw(message)
      setResult(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="form">
        <p className="muted">
          Постави пълния JSON на едно съобщение (без "messages" wrapper-а) — изпраща се директно към Infobip Messages API.
        </p>
        <textarea
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          className="doc-editor"
          spellCheck={false}
        />
        <button type="submit" disabled={sending}>{sending ? "Изпраща се..." : "Изпрати raw"}</button>
      </form>

      {error && <p className="error">Грешка: {error}</p>}
      {result && <pre className="result">{JSON.stringify(result, null, 2)}</pre>}
    </>
  )
}

export default function Notify() {
  const [mode, setMode] = useState("template")

  return (
    <div className="fade-in">
      <h2>Изпрати Notify</h2>

      <div className="tabs">
        <button className={mode === "template" ? "tab active" : "tab"} onClick={() => setMode("template")}>Template</button>
        <button className={mode === "raw" ? "tab active" : "tab"} onClick={() => setMode("raw")}>Custom JSON</button>
      </div>

      {mode === "template" ? <TemplateForm /> : <RawJsonForm />}
    </div>
  )
}
