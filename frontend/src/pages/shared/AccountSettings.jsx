import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { del, get, put, clearToken } from "../../api/client"
import { t } from "../../i18n"

export default function AccountSettings() {
  const navigate = useNavigate()

  const [email, setEmail] = useState("")
  const [fullName, setFullName] = useState("")
  const [profileMessage, setProfileMessage] = useState(null)
  const [profileError, setProfileError] = useState(null)
  const [savingProfile, setSavingProfile] = useState(false)

  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [passwordMessage, setPasswordMessage] = useState(null)
  const [passwordError, setPasswordError] = useState(null)
  const [savingPassword, setSavingPassword] = useState(false)

  const [deactivating, setDeactivating] = useState(false)

  useEffect(() => {
    get("/auth/me").then((data) => {
      setEmail(data.email)
      setFullName(data.full_name)
    })
  }, [])

  async function handleProfileSubmit(event) {
    event.preventDefault()
    setProfileError(null)
    setProfileMessage(null)
    setSavingProfile(true)

    try {
      await put("/auth/me", { full_name: fullName })
      setProfileMessage(t.account.profileSaved)
    } catch (err) {
      setProfileError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setSavingProfile(false)
    }
  }

  async function handlePasswordSubmit(event) {
    event.preventDefault()
    setPasswordError(null)
    setPasswordMessage(null)
    setSavingPassword(true)

    try {
      await put("/auth/me/password", {
        current_password: currentPassword,
        new_password: newPassword,
      })
      setCurrentPassword("")
      setNewPassword("")
      setPasswordMessage(t.account.passwordSaved)
    } catch (err) {
      setPasswordError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setSavingPassword(false)
    }
  }

  async function handleDeactivate() {
    if (!window.confirm(t.account.deactivateConfirm)) {
      return
    }

    setDeactivating(true)

    try {
      await del("/auth/me")
      clearToken()
      navigate("/login")
    } catch (err) {
      setProfileError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
      setDeactivating(false)
    }
  }

  return (
    <div className="mx-auto max-w-lg p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">{t.account.title}</h1>

      <form
        onSubmit={handleProfileSubmit}
        className="mb-8 space-y-3 rounded-lg bg-slate-800 p-6"
      >
        <h2 className="text-lg font-medium text-white">{t.account.profile}</h2>

        {profileError && (
          <p className="text-sm text-red-400">{profileError}</p>
        )}
        {profileMessage && (
          <p className="text-sm text-green-400">{profileMessage}</p>
        )}

        <input
          type="email"
          value={email}
          disabled
          className="w-full rounded bg-slate-900 px-3 py-2 text-slate-500"
        />

        <input
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder={t.auth.fullName}
          required
          minLength={2}
          className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
        />

        <button
          type="submit"
          disabled={savingProfile}
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {savingProfile ? t.common.saving : t.common.save}
        </button>
      </form>

      <form
        onSubmit={handlePasswordSubmit}
        className="mb-8 space-y-3 rounded-lg bg-slate-800 p-6"
      >
        <h2 className="text-lg font-medium text-white">
          {t.account.changePassword}
        </h2>

        {passwordError && (
          <p className="text-sm text-red-400">{passwordError}</p>
        )}
        {passwordMessage && (
          <p className="text-sm text-green-400">{passwordMessage}</p>
        )}

        <input
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          placeholder={t.account.currentPassword}
          required
          className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
        />

        <input
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          placeholder={t.account.newPassword}
          required
          minLength={8}
          className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
        />

        <button
          type="submit"
          disabled={savingPassword}
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {savingPassword ? t.common.saving : t.account.changePassword}
        </button>
      </form>

      <div className="rounded-lg bg-slate-800 p-6">
        <h2 className="mb-3 text-lg font-medium text-white">
          {t.account.dangerZone}
        </h2>
        <p className="mb-3 text-sm text-slate-400">
          {t.account.deactivateHint}
        </p>
        <button
          type="button"
          onClick={handleDeactivate}
          disabled={deactivating}
          className="rounded bg-red-700 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {deactivating ? t.account.deactivating : t.account.deactivate}
        </button>
      </div>
    </div>
  )
}