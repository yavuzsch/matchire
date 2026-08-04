import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"

import { get, post, setToken } from "../../api/client"

export default function Login() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const data = await post("/auth/login", { email, password })
      setToken(data.access_token)

      const me = await get("/auth/me")
      localStorage.setItem("role", me.role)

      navigate(me.role === "employer" ? "/employer" : "/candidate")
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 rounded-lg bg-slate-800 p-8"
      >
        <h1 className="text-2xl font-bold text-white">Giriş Yap</h1>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="E-posta"
          required
          className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
        />

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Şifre"
          required
          className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-blue-600 py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? "Giriş yapılıyor..." : "Giriş Yap"}
        </button>

        <p className="text-sm text-slate-400">
          Hesabınız yok mu?{" "}
          <Link to="/register" className="text-blue-400">
            Kayıt olun
          </Link>
        </p>
      </form>
    </div>
  )
}