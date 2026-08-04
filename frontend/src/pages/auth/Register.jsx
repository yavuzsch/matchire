import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"

import { post, setToken } from "../../api/client"

export default function Register() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [fullName, setFullName] = useState("")
  const [role, setRole] = useState("candidate")
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

      navigate(role === "employer" ? "/employer" : "/candidate")
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
        <h1 className="text-2xl font-bold text-white">Kayıt Ol</h1>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <input
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Ad Soyad"
          required
          className="w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"
        />

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

        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="w-full rounded bg-slate-700 px-3 py-2 text-white"
        >
          <option value="candidate">Aday</option>
          <option value="employer">İşveren</option>
        </select>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-blue-600 py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? "Kaydediliyor..." : "Kayıt Ol"}
        </button>

        <p className="text-sm text-slate-400">
          Zaten hesabınız var mı?{" "}
          <Link to="/login" className="text-blue-400">
            Giriş yapın
          </Link>
        </p>
      </form>
    </div>
  )
}