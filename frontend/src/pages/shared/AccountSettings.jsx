import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

import { del, get, put, clearToken } from "../../api/client"
import { Field, inputClass, Section } from "../../components/FormElements"
import Message from "../../components/Message"
import Spinner from "../../components/Spinner"
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
  const [newPasswordTouched, setNewPasswordTouched] = useState(false)
  const [passwordMessage, setPasswordMessage] = useState(null)
  const [passwordError, setPasswordError] = useState(null)
  const [savingPassword, setSavingPassword] = useState(false)

  const [deactivating, setDeactivating] = useState(false)

  const newPasswordTooShort =
    newPasswordTouched && newPassword.length > 0 && newPassword.length < 8

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
      setNewPasswordTouched(false)
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
    <div className="max-w-lg space-y-6">
      <h1 className="text-2xl font-extrabold text-ink">{t.account.title}</h1>

      <form onSubmit={handleProfileSubmit}>
        <Section title={t.account.profile}>
          <Message error={profileError} info={profileMessage} />

          <Field label={t.auth.email}>
            <input
              type="email"
              value={email}
              disabled
              className="w-full rounded-lg bg-surface-2 px-3 py-2 text-sm text-ink-soft opacity-60"
            />
          </Field>

          <Field label={t.auth.fullName}>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              minLength={2}
              className={inputClass}
            />
          </Field>

          <button
            type="submit"
            disabled={savingProfile}
            className="flex items-center gap-2 rounded-lg bg-blue-500 px-6 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
          >
            {savingProfile && <Spinner />}
            {savingProfile ? t.common.saving : t.common.save}
          </button>
        </Section>
      </form>

      <form onSubmit={handlePasswordSubmit}>
        <Section title={t.account.changePassword}>
          <Message error={passwordError} info={passwordMessage} />

          <Field label={t.account.currentPassword}>
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
              className={inputClass}
            />
          </Field>

          <Field label={t.account.newPassword}>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              onBlur={() => setNewPasswordTouched(true)}
              required
              minLength={8}
              className={`w-full rounded-lg bg-surface-2 px-3 py-2 text-sm text-ink placeholder-ink-soft outline-none ring-2 focus:ring-2 ${
                newPasswordTooShort ? "ring-red-500" : "ring-blue-500"
              }`}
            />
            {newPasswordTooShort && (
              <p className="mt-1 text-xs text-red-400">
                {t.account.newPasswordTooShort}
              </p>
            )}
          </Field>

          <button
            type="submit"
            disabled={savingPassword}
            className="flex items-center gap-2 rounded-lg bg-blue-500 px-6 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
          >
            {savingPassword && <Spinner />}
            {savingPassword ? t.common.saving : t.account.changePassword}
          </button>
        </Section>
      </form>

      <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-6">
        <h2 className="font-semibold text-red-400">{t.account.dangerZone}</h2>
        <p className="mt-2 text-sm text-ink-soft">{t.account.deactivateHint}</p>
        <button
          type="button"
          onClick={handleDeactivate}
          disabled={deactivating}
          className="mt-4 flex items-center gap-2 rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-red-600 disabled:opacity-50"
        >
          {deactivating && <Spinner />}
          {deactivating ? t.account.deactivating : t.account.deactivate}
        </button>
      </div>
    </div>
  )
}