import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { authApi } from "../api"
import { useAuth } from "../auth/AuthContext"

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [step, setStep] = useState("credentials")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [otpId, setOtpId] = useState(null)
  const [code, setCode] = useState("")
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const handleCredentials = async (e) => {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const res = await authApi.login({ email, password })
      setOtpId(res.otp_id)
      setStep("otp")
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const handleVerify = async (e) => {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const res = await authApi.verify({ otp_id: otpId, code })
      login(res.token, res.user)
      navigate("/")
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Viber Bot Dashboard</h1>

        {step === "credentials" && (
          <form onSubmit={handleCredentials} className="form">
            <input type="email" placeholder="Имейл" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <input type="password" placeholder="Парола" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <button type="submit" disabled={busy}>Влез</button>
          </form>
        )}

        {step === "otp" && (
          <form onSubmit={handleVerify} className="form">
            <p>Изпратихме код за вход през Viber на регистрирания телефон.</p>
            <input placeholder="6-цифрен код" value={code} onChange={(e) => setCode(e.target.value)} required />
            <button type="submit" disabled={busy}>Потвърди</button>
          </form>
        )}

        {error && <p className="error">{error}</p>}

        <p>Нямаш акаунт? <Link to="/register">Регистрирай се</Link></p>
      </div>
    </div>
  )
}
