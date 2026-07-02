import { useState } from "react"
import { api } from "../api"

const LANGUAGES = [
  { code: "bg", label: "Български" },
  { code: "en", label: "English" },
  { code: "de", label: "Deutsch" },
  { code: "fr", label: "Français" },
  { code: "ru", label: "Русский" },
]

export default function Voice() {
  const [to, setTo] = useState("")
  const [text, setText] = useState("Здравейте! Обажда се системата на Infobip TC Partners. Имате нова нотификация.")
  const [language, setLanguage] = useState("bg")
  const [speechRate, setSpeechRate] = useState(0.9)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [sending, setSending] = useState(false)
  const [history, setHistory] = useState([])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    setSending(true)
    try {
      const res = await api.voiceCall({ to, text, language, speech_rate: speechRate })
      setResult(res)
      setHistory((prev) => [
        { to, text: text.slice(0, 60) + (text.length > 60 ? "..." : ""), time: new Date().toLocaleTimeString("bg-BG"), status: res.infobip_status },
        ...prev.slice(0, 9),
      ])
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  const charCount = text.length

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Voice обаждания</h2>
        <span className="badge" title="Number ID">+359 2 408 5301</span>
      </div>

      <div className="voice-layout">
        <div className="settings-card" style={{ maxWidth: 460 }}>
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
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={4}
              required
            />
            <span className="muted" style={{ fontSize: 12 }}>{charCount} символа</span>

            <label>Език</label>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>{l.label}</option>
              ))}
            </select>

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

            <button type="submit" disabled={sending} style={{ marginTop: 8 }}>
              {sending ? "Обажда се..." : "📞 Обади се"}
            </button>
          </form>

          {error && <p className="error" style={{ marginTop: 12 }}>Грешка: {error}</p>}
          {result && (
            <div className="success" style={{ marginTop: 12, padding: "8px 12px", borderRadius: 8 }}>
              ✅ Обаждането е прието (status {result.infobip_status})
            </div>
          )}
        </div>

        {history.length > 0 && (
          <div style={{ flex: 1, minWidth: 0 }}>
            <h3>История</h3>
            <table>
              <thead>
                <tr><th>Час</th><th>До</th><th>Текст</th><th>Статус</th></tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i}>
                    <td className="muted">{h.time}</td>
                    <td>{h.to}</td>
                    <td className="muted">{h.text}</td>
                    <td>{h.status === 200 ? "✅" : "❌"}</td>
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
