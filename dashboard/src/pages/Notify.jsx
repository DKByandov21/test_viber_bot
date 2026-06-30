import { useEffect, useState } from "react"
import { api } from "../api"
import { dateRange, formatDateDMY } from "../utils/time"

const RAW_PLACEHOLDER = `{
  "channel": "VIBER_BM",
  "sender": "TCP",
  "destinations": [{"to": "359876888400"}],
  "template": {"templateName": "110d2698-1ea9-4b9b-b9e1-2ec38afa008f", "language": "bg"},
  "content": {
    "body": {
      "type": "TEXT",
      "p1": "50100000001",
      "p2": "15.07.2026",
      "p3": "Александър Табаков"
    }
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
  const [repeat, setRepeat] = useState(1)
  const [dateMode, setDateMode] = useState(false)
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [results, setResults] = useState([])
  const [error, setError] = useState(null)
  const [sending, setSending] = useState(false)

  const sendOne = async (rawText) => {
    const message = JSON.parse(rawText)
    return api.notifyRaw(message)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setResults([])

    if (dateMode) {
      if (!startDate || !endDate) {
        setError("Избери начална и крайна дата")
        return
      }
      if (!raw.includes("{{DATE}}")) {
        setError('Сложи плейсхолдъра {{DATE}} някъде в JSON-а (напр. като стойност на p2)')
        return
      }
      const dates = dateRange(startDate, endDate)
      if (dates.length > 60) {
        setError("Диапазонът е твърде голям (макс. 60 дни)")
        return
      }

      setSending(true)
      try {
        const collected = []
        for (const d of dates) {
          const formatted = formatDateDMY(d)
          try {
            const res = await sendOne(raw.replaceAll("{{DATE}}", formatted))
            collected.push({ date: formatted, ...res })
          } catch (err) {
            collected.push({ date: formatted, status: "error", message: err.message })
          }
          setResults([...collected])
        }
      } finally {
        setSending(false)
      }
      return
    }

    try {
      JSON.parse(raw)
    } catch {
      setError("Невалиден JSON")
      return
    }

    const count = Math.max(1, Math.min(50, parseInt(repeat, 10) || 1))

    setSending(true)
    try {
      const collected = []
      for (let i = 0; i < count; i++) {
        try {
          const res = await sendOne(raw)
          collected.push({ attempt: i + 1, ...res })
        } catch (err) {
          collected.push({ attempt: i + 1, status: "error", message: err.message })
        }
        setResults([...collected])
      }
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="form">
        <p className="muted">
          Постави пълния JSON на едно съобщение (без "messages" wrapper-а) — изпраща се директно към Infobip Messages API.
          За няколко получателя добави повече записи в "destinations".
        </p>
        <textarea
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          className="doc-editor"
          spellCheck={false}
        />

        <label>
          <input type="checkbox" checked={dateMode} onChange={(e) => setDateMode(e.target.checked)} style={{ width: "auto", marginRight: 6 }} />
          Debug по дати (изпрати веднъж на ден за диапазон)
        </label>

        {dateMode ? (
          <>
            <p className="muted">Сложи <code>{"{{DATE}}"}</code> в JSON-а където да отиде датата (формат 12.02.2026).</p>
            <label>От дата</label>
            <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            <label>До дата</label>
            <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </>
        ) : (
          <>
            <label>Брой повторения (1-50)</label>
            <input type="number" min={1} max={50} value={repeat} onChange={(e) => setRepeat(e.target.value)} />
          </>
        )}

        <button type="submit" disabled={sending}>
          {sending ? "Изпраща се..." : dateMode ? "Изпрати по дати" : repeat > 1 ? `Изпрати ${repeat} пъти` : "Изпрати raw"}
        </button>
      </form>

      {error && <p className="error">Грешка: {error}</p>}
      {results.length > 0 && (
        <pre className="result">{JSON.stringify(results, null, 2)}</pre>
      )}
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
