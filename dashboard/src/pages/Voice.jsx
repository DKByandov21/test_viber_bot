import { useRef, useState } from "react"
import { api } from "../api"

const LANGUAGES = [
  { code: "bg", label: "Български" },
  { code: "en", label: "English" },
  { code: "de", label: "Deutsch" },
  { code: "fr", label: "Français" },
  { code: "ru", label: "Русский" },
]

const SSML_SNIPPETS = [
  { label: "Пауза 500ms", insert: '<break time="500ms"/>' },
  { label: "Пауза 1s", insert: '<break time="1s"/>' },
  { label: "Акцент", insert: '<emphasis level="strong">|</emphasis>', cursor: true },
  { label: "Бавно", insert: '<prosody rate="slow">|</prosody>', cursor: true },
  { label: "Бързо", insert: '<prosody rate="fast">|</prosody>', cursor: true },
  { label: "Висок тон", insert: '<prosody pitch="high">|</prosody>', cursor: true },
  { label: "Нисък тон", insert: '<prosody pitch="low">|</prosody>', cursor: true },
  { label: "Силно", insert: '<prosody volume="loud">|</prosody>', cursor: true },
  { label: "Тихо", insert: '<prosody volume="soft">|</prosody>', cursor: true },
]

export default function Voice() {
  const [to, setTo] = useState("")
  const [text, setText] = useState("Здравейте! Обажда се системата на Infobip TC Partners. Имате нова нотификация.")
  const [language, setLanguage] = useState("bg")
  const [speechRate, setSpeechRate] = useState(0.9)
  const [gender, setGender] = useState("")
  const [pause, setPause] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [sending, setSending] = useState(false)
  const [history, setHistory] = useState([])
  const textareaRef = useRef(null)

  const insertSsml = (snippet) => {
    const el = textareaRef.current
    if (!el) return
    const start = el.selectionStart
    const end = el.selectionEnd
    const selected = text.slice(start, end)

    let toInsert
    if (snippet.cursor) {
      // replace | with selected text or leave cursor there
      toInsert = snippet.insert.replace("|", selected || "")
    } else {
      toInsert = snippet.insert
    }

    const newText = text.slice(0, start) + toInsert + text.slice(end)
    setText(newText)

    // restore focus + set cursor after inserted text
    setTimeout(() => {
      el.focus()
      const cursorPos = start + toInsert.length
      el.setSelectionRange(cursorPos, cursorPos)
    }, 0)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    setSending(true)
    try {
      const payload = { to, text, language, speech_rate: speechRate }
      if (gender) payload.gender = gender
      if (pause > 0) payload.pause = pause
      const res = await api.voiceCall(payload)
      setResult(res)
      setHistory((prev) => [
        {
          to,
          text: text.slice(0, 60) + (text.length > 60 ? "..." : ""),
          time: new Date().toLocaleTimeString("bg-BG"),
          status: res.infobip_status,
          gender: gender || "—",
        },
        ...prev.slice(0, 9),
      ])
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Voice обаждания</h2>
        <span className="badge" title="Caller number">+359 2 408 5301</span>
      </div>

      <div className="voice-layout">
        <div className="settings-card" style={{ maxWidth: 520 }}>
          <h3>Ново обаждане</h3>
          <form onSubmit={handleSubmit} className="form">

            <label>До (телефон)</label>
            <input
              placeholder="359876888400"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              required
            />

            <label>Текст за изговаряне</label>
            {/* SSML toolbar */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 4 }}>
              {SSML_SNIPPETS.map((s) => (
                <button
                  key={s.label}
                  type="button"
                  className="secondary"
                  style={{ fontSize: 11, padding: "2px 7px" }}
                  onClick={() => insertSsml(s)}
                  title={s.insert}
                >
                  {s.label}
                </button>
              ))}
            </div>
            <textarea
              ref={textareaRef}
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={5}
              required
              style={{ fontFamily: "monospace", fontSize: 13 }}
            />
            <span className="muted" style={{ fontSize: 12 }}>{text.length} символа</span>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <label>Език</label>
                <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                  {LANGUAGES.map((l) => (
                    <option key={l.code} value={l.code}>{l.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label>Пол на гласа</label>
                <select value={gender} onChange={(e) => setGender(e.target.value)}>
                  <option value="">Автоматично</option>
                  <option value="female">Женски</option>
                  <option value="male">Мъжки</option>
                </select>
              </div>
            </div>

            <label>Скорост на говор ({speechRate}x)</label>
            <input
              type="range"
              min={0.5} max={2.0} step={0.1}
              value={speechRate}
              onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
            />
            <div className="muted" style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
              <span>0.5x (бавно)</span><span>1.0x (нормално)</span><span>2.0x (бързо)</span>
            </div>

            <label>Пауза преди старт (сек: {pause})</label>
            <input
              type="range"
              min={0} max={10} step={1}
              value={pause}
              onChange={(e) => setPause(parseInt(e.target.value))}
            />
            <div className="muted" style={{ display: "flex", justifyContent: "space-between", fontSize: 12 }}>
              <span>0s</span><span>5s</span><span>10s</span>
            </div>

            <button type="submit" disabled={sending} style={{ marginTop: 8 }}>
              {sending ? "Обажда се..." : "📞 Обади се"}
            </button>
          </form>

          {error && <p className="error" style={{ marginTop: 12 }}>Грешка: {error}</p>}
          {result && (
            <div className="success" style={{ marginTop: 12, padding: "8px 12px", borderRadius: 8 }}>
              ✅ Обаждането е прието (HTTP {result.infobip_status})
            </div>
          )}

          <details style={{ marginTop: 16 }}>
            <summary className="muted" style={{ cursor: "pointer", fontSize: 13 }}>SSML — как да форматираш текста</summary>
            <div style={{ marginTop: 8, fontSize: 12, lineHeight: 1.7 }}>
              <p>Можеш да поставяш SSML тагове директно в текста:</p>
              <ul style={{ paddingLeft: 16 }}>
                <li><code>{'<break time="500ms"/>'}</code> — пауза 500мс</li>
                <li><code>{'<emphasis level="strong">дума</emphasis>'}</code> — акцент</li>
                <li><code>{'<prosody rate="slow">текст</prosody>'}</code> — по-бавно произношение</li>
                <li><code>{'<prosody pitch="high">текст</prosody>'}</code> — по-висок тон</li>
                <li><code>{'<prosody volume="loud">текст</prosody>'}</code> — по-силен звук</li>
              </ul>
              <p className="muted">Маркирай дума и натисни бутон за бързо вмъкване.</p>
            </div>
          </details>
        </div>

        {history.length > 0 && (
          <div style={{ flex: 1, minWidth: 0 }}>
            <h3>История</h3>
            <table>
              <thead>
                <tr><th>Час</th><th>До</th><th>Пол</th><th>Текст</th><th>Статус</th></tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i}>
                    <td className="muted">{h.time}</td>
                    <td>{h.to}</td>
                    <td className="muted">{h.gender}</td>
                    <td className="muted" style={{ fontFamily: "monospace", fontSize: 12 }}>{h.text}</td>
                    <td>{h.status === 200 ? "✅" : `❌ ${h.status}`}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
