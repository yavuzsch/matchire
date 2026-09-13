import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"

import { post, setToken } from "../../api/client"
import BrandPanel from "../../components/BrandPanel"
import { authInputClass } from "../../components/FormElements"
import LanguageToggle from "../../components/LanguageToggle"
import Message from "../../components/Message"
import Spinner from "../../components/Spinner"
import { t } from "../../i18n"

export default function Register() {
  const navigate = useNavigate()
  const [role, setRole] = useState(null)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [passwordTouched, setPasswordTouched] = useState(false)
  const [fullName, setFullName] = useState("")
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const passwordTooShort =
    passwordTouched && password.length > 0 && password.length < 8

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const data = await post("/auth/register", {
        email,
        password,
        full_name: fullName,
        role,
      })
      setToken(data.access_token)
      localStorage.setItem("role", role)
      navigate(role === "employer" ? "/employer/jobs" : "/candidate/jobs")
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-screen">
      <BrandPanel
        title={t.auth.registerPanelTitle}
        description={t.auth.registerPanelDescription}
      />

      <LanguageToggle className="absolute right-6 top-6" />

      <div className="flex flex-1 items-center justify-center bg-base px-6">
        {!role ? (
          <div className="w-full max-w-sm">
            <h1 className="text-2xl font-extrabold text-ink">{t.auth.register}</h1>
            <p className="mt-1 text-sm text-ink-soft">{t.auth.chooseRole}</p>

            <div className="mt-6 space-y-3">
              <button
                type="button"
                onClick={() => setRole("candidate")}
                className="flex w-full items-center justify-between rounded-lg bg-surface-2 px-4 py-3.5 text-sm font-semibold text-ink transition-colors hover:bg-blue-600/20"
              >
                {t.auth.registerAsCandidate}
                <span className="text-blue-400">→</span>
              </button>
              <button
                type="button"
                onClick={() => setRole("employer")}
                className="flex w-full items-center justify-between rounded-lg bg-surface-2 px-4 py-3.5 text-sm font-semibold text-ink transition-colors hover:bg-blue-600/20"
              >
                {t.auth.registerAsEmployer}
                <span className="text-blue-400">→</span>
              </button>
            </div>

            <p className="mt-6 text-sm text-ink-soft">
              {t.auth.hasAccount}{" "}
              <Link to="/login" className="font-semibold text-blue-400 hover:text-blue-500">
                {t.auth.goLogin}
              </Link>
            </p>
          </div>
        ) : (
          <div className="w-full max-w-sm">
            <button
              type="button"
              onClick={() => setRole(null)}
              className="text-sm text-ink-soft hover:text-ink"
            >
              ← {t.auth.changeRole}
            </button>

            <h1 className="mt-4 text-2xl font-extrabold text-ink">
              {role === "employer" ? t.auth.registerAsEmployer : t.auth.registerAsCandidate}
            </h1>

            <Message error={error} className="mt-3" />

            <form onSubmit={handleSubmit} className="mt-6 space-y-3">
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder={t.auth.fullName}
                required
                className={authInputClass}
              />

              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t.auth.email}
                required
                className={authInputClass}
              />

              <div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onBlur={() => setPasswordTouched(true)}
                  placeholder={t.auth.password}
                  required
                  minLength={8}
                  className={`${authInputClass} ring-2 ${
                    passwordTooShort ? "ring-red-500" : "ring-blue-500"
                  }`}
                />
                {passwordTooShort && (
                  <p className="mt-1 text-xs text-red-400">
                    {t.auth.passwordTooShort}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-500 py-3 text-sm font-bold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
              >
                {loading && <Spinner />}
                {loading ? t.auth.registering : t.auth.register}
              </button>
            </form>

            <p className="mt-6 text-sm text-ink-soft">
              {t.auth.hasAccount}{" "}
              <Link to="/login" className="font-semibold text-blue-400 hover:text-blue-500">
                {t.auth.goLogin}
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}