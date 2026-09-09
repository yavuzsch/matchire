import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"

import { get, post, setToken } from "../../api/client"
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
      if (err.code === "ACCOUNT_DEACTIVATED") {
        setShowReactivate(true)
      }
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

  if (!role) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-900 px-4">
        <div className="w-full max-w-sm space-y-4 rounded-lg bg-slate-800 p-8">
          <h1 className="text-2xl font-bold text-white">{t.auth.login}</h1>
          <p className="text-sm text-slate-400">{t.auth.chooseRole}</p>

          <div className="space-y-3">
            {ROLES.map((item) => (
              <button
                key={item.value}
                type="button"
                onClick={() => setRole(item.value)}
                className="w-full rounded bg-slate-700 py-3 font-medium text-white hover:bg-slate-600"
              >
                {item.label}
              </button>
            ))}
          </div>

          <p className="text-sm text-slate-400">
            {t.auth.noAccount}{" "}
            <Link to="/register" className="text-blue-400">
              {t.auth.goRegister}
            </Link>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 rounded-lg bg-slate-800 p-8"
      >
        <button
          type="button"
          onClick={() => setRole(null)}
          className="text-sm text-slate-400"
        >
          ← {t.auth.changeRole}
        </button>

        <h1 className="text-2xl font-bold text-white">
          {role === "employer" ? t.auth.employerLogin : t.auth.candidateLogin}
        </h1>

        {error && <p className="text-sm text-red-400">{error}</p>}

        {showReactivate && (
          <button
            type="button"
            onClick={handleReactivate}
            disabled={reactivating}
            className="w-full rounded bg-amber-600 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {reactivating ? t.auth.reactivating : t.auth.reactivate}
          </button>
        )}

        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={t.auth.email}
          required
          className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
        />

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={t.auth.password}
          required
          className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-blue-600 py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? t.auth.loggingIn : t.auth.login}
        </button>

        <p className="text-sm text-slate-400">
          {t.auth.noAccount}{" "}
          <Link to="/register" className="text-blue-400">
            {t.auth.goRegister}
          </Link>
        </p>
      </form>
    </div>
  )
}