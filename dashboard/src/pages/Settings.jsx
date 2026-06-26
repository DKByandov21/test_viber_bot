import { useState } from "react"
import { authApi } from "../api"
import { useAuth } from "../auth/AuthContext"

export default function Settings() {
  const { user, setUser } = useAuth()

  const [phone, setPhone] = useState(user?.phone || "")
  const [phoneStatus, setPhoneStatus] = useState(null)
  const [phoneError, setPhoneError] = useState(null)

  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [passwordStatus, setPasswordStatus] = useState(null)
  const [passwordError, setPasswordError] = useState(null)

  const handlePhoneSubmit = async (e) => {
    e.preventDefault()
    setPhoneError(null)
    setPhoneStatus(null)
    try {
      const updated = await authApi.updateMe({ phone })
      setUser(updated)
      setPhoneStatus("Телефонът е обновен.")
    } catch (err) {
      setPhoneError(err.message)
    }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    setPasswordError(null)
    setPasswordStatus(null)

    if (newPassword !== confirmPassword) {
      setPasswordError("Новите пароли не съвпадат")
      return
    }

    try {
      await authApi.updateMe({ current_password: currentPassword, new_password: newPassword })
      setPasswordStatus("Паролата е сменена успешно.")
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
    } catch (err) {
      setPasswordError(err.message)
    }
  }

  return (
    <div className="fade-in">
      <h2>Настройки на профила</h2>

      <div className="settings-card">
        <h3>Профил</h3>
        <p className="muted">{user?.email}</p>
        <form onSubmit={handlePhoneSubmit} className="form">
          <label>Телефон за Viber OTP</label>
          <input value={phone} onChange={(e) => setPhone(e.target.value)} required />
          <button type="submit">Запази телефона</button>
        </form>
        {phoneStatus && <p className="success">{phoneStatus}</p>}
        {phoneError && <p className="error">{phoneError}</p>}
      </div>

      <div className="settings-card">
        <h3>Смяна на парола</h3>
        <form onSubmit={handlePasswordSubmit} className="form">
          <label>Текуща парола</label>
          <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} required />
          <label>Нова парола</label>
          <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required minLength={6} />
          <label>Потвърди новата парола</label>
          <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required minLength={6} />
          <button type="submit">Смени паролата</button>
        </form>
        {passwordStatus && <p className="success">{passwordStatus}</p>}
        {passwordError && <p className="error">{passwordError}</p>}
      </div>
    </div>
  )
}
