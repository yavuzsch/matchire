import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"

import { post, setToken } from "../../api/client"
import { t } from "../../i18n"

export default function Register() {
  const navigate = useNavigate()
  const [role, setRole] = useState(null)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [fullName, setFullName] = useState("")
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

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

  if (!role) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-900 px-4">
        <div className="w-full max-w-sm space-y-4 rounded-lg bg-slate-800 p-8">
          <h1 className="text-2xl font-bold text-white">{t.auth.register}</h1>
          <p className="text-sm text-slate-400">{t.auth.chooseRole}</p>

          <div className="space-y-3">
            <button
              type="button"
              onClick={() => setRole("candidate")}
              className="w-full rounded bg-slate-700 py-3 font-medium text-white hover:bg-slate-600"
            >
              {t.auth.registerAsCandidate}
            </button>
            <button
              type="button"
              onClick={() => setRole("employer")}
              className="w-full rounded bg-slate-700 py-3 font-medium text-white hover:bg-slate-600"
            >
              {t.auth.registerAsEmployer}
            </button>
          </div>

          <p className="text-sm text-slate-400">
            {t.auth.hasAccount}{" "}
            <Link to="/login" className="text-blue-400">
              {t.auth.goLogin}
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
          {role === "employer"
            ? t.auth.registerAsEmployer
            : t.auth.registerAsCandidate}
        </h1>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <input
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder={t.auth.fullName}
          required
          className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
        />

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
          minLength={8}
          className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-blue-600 py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? t.auth.registering : t.auth.register}
        </button>

        <p className="text-sm text-slate-400">
          {t.auth.hasAccount}{" "}
          <Link to="/login" className="text-blue-400">
            {t.auth.goLogin}
          </Link>
        </p>
      </form>
    </div>
  )
}