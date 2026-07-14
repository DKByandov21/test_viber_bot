import { useEffect, useMemo, useState } from "react"
import { api } from "../api"
import { dateRange, formatDateDMY, parseDateDMY } from "../utils/time"

function findDateParams(rawText) {
  try {
    const parsed = JSON.parse(rawText)
    const containers = ["body", "parameters"]
    const found = []
    for (const container of containers) {
      const obj = parsed?.content?.[container]
      if (obj && typeof obj === "object") {
        for (const key of Object.keys(obj)) {
          if (key === "type") continue
          found.push({ container, key })
        }
      }
    }
    return found
  } catch {
    return []
  }
}

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
  const [dateParam, setDateParam] = useState("")
  const [startDateText, setStartDateText] = useState("")
  const [endDateText, setEndDateText] = useState("")
  const [results, setResults] = useState([])
  const [error, setError] = useState(null)
  const [sending, setSending] = useState(false)

  const dateParamOptions = useMemo(() => findDateParams(raw), [raw])

  const sendOne = async (message) => api.notifyRaw(message)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setResults([])

    if (dateMode) {
      if (!dateParam) {
        setError("Избери кой параметър да варира по дата")
        return
      }
      const start = parseDateDMY(startDateText)
      const end = parseDateDMY(endDateText)
      if (!start || !end) {
        setError("Датите трябва да са във формат ДД.ММ.ГГГГ")
        return
      }
      if (start > end) {
        setError("Началната дата трябва да е преди крайната")
        return
      }

      const dates = dateRange(start, end)
      if (dates.length > 60) {
        setError("Диапазонът е твърде голям (макс. 60 дни)")
        return
      }

      let baseMessage
      try {
        baseMessage = JSON.parse(raw)
      } catch {
        setError("Невалиден JSON")
        return
      }

      const [container, key] = dateParam.split(".")

      setSending(true)
      try {
        const collected = []
        for (const d of dates) {
          const formatted = formatDateDMY(d)
          const message = JSON.parse(JSON.stringify(baseMessage))
          message.content[container][key] = formatted
          try {
            const res = await sendOne(message)
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

    let message
    try {
      message = JSON.parse(raw)
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
          const res = await sendOne(message)
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
          Debug по дати (изпраща по едно съобщение веднага за всяка дата от диапазона)
        </label>

        {dateMode ? (
          <>
            <label>Параметър, който да варира по дата</label>
            <select value={dateParam} onChange={(e) => setDateParam(e.target.value)}>
              <option value="">-- избери параметър --</option>
              {dateParamOptions.map((opt) => (
                <option key={`${opt.container}.${opt.key}`} value={`${opt.container}.${opt.key}`}>
                  {opt.container}.{opt.key}
                </option>
              ))}
            </select>

            <label>От дата (ДД.ММ.ГГГГ)</label>
            <input placeholder="12.02.2026" value={startDateText} onChange={(e) => setStartDateText(e.target.value)} />
            <label>До дата (ДД.ММ.ГГГГ)</label>
            <input placeholder="24.02.2026" value={endDateText} onChange={(e) => setEndDateText(e.target.value)} />
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

function BulkForm() {
  const [templates, setTemplates] = useState([])
  const [templateKey, setTemplateKey] = useState("")
  const [placeholders, setPlaceholders] = useState({})
  const [numbersText, setNumbersText] = useState("")
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [sending, setSending] = useState(false)

  useEffect(() => {
    api.listTemplates().then(setTemplates).catch((e) => setError(e.message))
  }, [])

  const selected = templates.find((t) => t.key === templateKey)

  const toList = numbersText
    .split(/[\n,;]+/)
    .map((s) => s.trim())
    .filter(Boolean)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!toList.length) { setError("Въведи поне един номер"); return }
    setError(null)
    setResults(null)
    setSending(true)
    try {
      const res = await api.notifyBulk({ template: templateKey, to_list: toList, placeholders })
      setResults(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="form">
        <label>Template</label>
        <select value={templateKey} onChange={(e) => { setTemplateKey(e.target.value); setPlaceholders({}) }} required>
          <option value="">-- избери template --</option>
          {templates.map((t) => (
            <option key={t.key} value={t.key}>{t.key}{t.description ? ` — ${t.description}` : ""}</option>
          ))}
        </select>

        {selected && (selected.params || []).length > 0 && (
          <>
            <label>Placeholder стойности (общи за всички получатели)</label>
            {(selected.params || []).map((p) => (
              <div key={p} style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <span className="badge" style={{ minWidth: 32, textAlign: "center" }}>{p}</span>
                <input
                  placeholder={`Стойност за ${p}`}
                  value={placeholders[p] || ""}
                  onChange={(ev) => setPlaceholders({ ...placeholders, [p]: ev.target.value })}
                  style={{ flex: 1 }}
                />
              </div>
            ))}
          </>
        )}

        <label>Номера за изпращане</label>
        <p className="muted" style={{ fontSize: 12, margin: "0 0 4px" }}>
          Един на ред (или разделени с , или ;). Максимум 200.
        </p>
        <textarea
          value={numbersText}
          onChange={(e) => setNumbersText(e.target.value)}
          rows={6}
          placeholder={"359876888400\n359888123456\n359877999000"}
          style={{ fontFamily: "monospace" }}
        />
        {toList.length > 0 && (
          <span className="muted" style={{ fontSize: 12 }}>{toList.length} номера</span>
        )}

        <button type="submit" disabled={sending || !templateKey || !toList.length} style={{ marginTop: 8 }}>
          {sending ? `Изпраща...` : `📤 Изпрати до ${toList.length || 0} получател${toList.length === 1 ? "я" : "и"}`}
        </button>
      </form>

      {error && <p className="error">Грешка: {error}</p>}

      {results && (
        <div style={{ marginTop: 16 }}>
          <div style={{ display: "flex", gap: 12, marginBottom: 12 }}>
            <span className="badge" style={{ background: "var(--success, #16a34a)", color: "#fff" }}>
              ✅ Изпратени: {results.sent}
            </span>
            <span className="badge" style={{ background: results.failed > 0 ? "var(--danger, #dc2626)" : undefined, color: results.failed > 0 ? "#fff" : undefined }}>
              ❌ Грешки: {results.failed}
            </span>
          </div>
          <table>
            <thead>
              <tr><th>Номер</th><th>HTTP</th><th>Статус</th></tr>
            </thead>
            <tbody>
              {results.results.map((r, i) => (
                <tr key={i}>
                  <td style={{ fontFamily: "monospace" }}>{r.to}</td>
                  <td>{r.status}</td>
                  <td>{r.ok ? "✅" : "❌"}{r.error ? ` ${r.error}` : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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
        <button className={mode === "bulk" ? "tab active" : "tab"} onClick={() => setMode("bulk")}>Bulk</button>
        <button className={mode === "raw" ? "tab active" : "tab"} onClick={() => setMode("raw")}>Custom JSON</button>
      </div>

      {mode === "template" && <TemplateForm />}
      {mode === "bulk" && <BulkForm />}
      {mode === "raw" && <RawJsonForm />}
    </div>
  )
}
