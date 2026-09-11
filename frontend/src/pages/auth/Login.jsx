import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"

import { get, post, setToken } from "../../api/client"
import BrandPanel from "../../components/BrandPanel"
import { authInputClass } from "../../components/FormElements"
import LanguageToggle from "../../components/LanguageToggle"
import Message from "../../components/Message"
import Spinner from "../../components/Spinner"
import { t } from "../../i18n"

const ROLES = [
  { value: "candidate", label: t.auth.candidate },
  { value: "employer", label: t.auth.employer },
]

export default function Login() {
  const navigate = useNavigate()
  const [role, setRole] = useState(null)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [reactivating, setReactivating] = useState(false)
  const [showReactivate, setShowReactivate] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setShowReactivate(false)
    setLoading(true)

    try {
      const data = await post("/auth/login", { email, password, role })
      setToken(data.access_token)
      const me = await get("/auth/me")
      localStorage.setItem("role", me.role)
      navigate(me.role === "employer" ? "/employer/jobs" : "/candidate/jobs")
    } catch (err) {
      if (err.code === "ACCOUNT_DEACTIVATED") setShowReactivate(true)
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setLoading(false)
    }
  }

  async function handleReactivate() {
    setError(null)
    setReactivating(true)

    try {
      const data = await post("/auth/reactivate", { email, password, role })
      setToken(data.access_token)
      const me = await get("/auth/me")
      localStorage.setItem("role", me.role)
      navigate(me.role === "employer" ? "/employer/jobs" : "/candidate/jobs")
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
      setShowReactivate(false)
    } finally {
      setReactivating(false)
    }
  }

  return (
    <div className="relative flex min-h-screen">
      <BrandPanel
        title={t.auth.loginPanelTitle}
        description={t.auth.loginPanelDescription}
      />

      <LanguageToggle className="absolute right-6 top-6" />

      <div className="flex flex-1 items-center justify-center bg-base px-6">
        {!role ? (
          <div className="w-full max-w-sm">
            <h1 className="text-2xl font-extrabold text-ink">{t.auth.login}</h1>
            <p className="mt-1 text-sm text-ink-soft">{t.auth.chooseRole}</p>

            <div className="mt-6 space-y-3">
              {ROLES.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  onClick={() => setRole(item.value)}
                  className="flex w-full items-center justify-between rounded-lg bg-surface-2 px-4 py-3.5 text-sm font-semibold text-ink transition-colors hover:bg-blue-600/20"
                >
                  {item.label}
                  <span className="text-blue-400">→</span>
                </button>
              ))}
            </div>

            <p className="mt-6 text-sm text-ink-soft">
              {t.auth.noAccount}{" "}
              <Link to="/register" className="font-semibold text-blue-400 hover:text-blue-500">
                {t.auth.goRegister}
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
              {role === "employer" ? t.auth.employerLogin : t.auth.candidateLogin}
            </h1>

            <Message error={error} className="mt-3" />

            {showReactivate && (
              <button
                type="button"
                onClick={handleReactivate}
                disabled={reactivating}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600/20 py-2.5 text-sm font-semibold text-blue-400 transition-colors hover:bg-blue-600/30 disabled:opacity-50"
              >
                {reactivating && <Spinner />}
                {reactivating ? t.auth.reactivating : t.auth.reactivate}
              </button>
            )}

            <form onSubmit={handleSubmit} className="mt-6 space-y-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t.auth.email}
                required
                className={authInputClass}
              />

              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={t.auth.password}
                required
                className={authInputClass}
              />

              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-500 py-3 text-sm font-bold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
              >
                {loading && <Spinner />}
                {loading ? t.auth.loggingIn : t.auth.login}
              </button>
            </form>

            <p className="mt-6 text-sm text-ink-soft">
              {t.auth.noAccount}{" "}
              <Link to="/register" className="font-semibold text-blue-400 hover:text-blue-500">
                {t.auth.goRegister}
              </Link>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}