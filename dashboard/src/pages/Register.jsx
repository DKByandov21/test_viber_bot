import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { authApi } from "../api"

export default function Register() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [phone, setPhone] = useState("")
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      await authApi.register({ email, password, phone })
      navigate("/login")
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Регистрация</h1>
        <form onSubmit={handleSubmit} className="form">
          <input type="email" placeholder="Имейл" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input type="password" placeholder="Парола" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
          <input placeholder="Телефон за Viber OTP (напр. 359...)" value={phone} onChange={(e) => setPhone(e.target.value)} required />
          <button type="submit" disabled={busy}>Регистрирай се</button>
        </form>

        {error && <p className="error">{error}</p>}

        <p>Вече имаш акаунт? <Link to="/login">Влез</Link></p>
      </div>
    </div>
  )
}
