import { Link, useNavigate } from "react-router-dom"

import { clearToken } from "../api/client"
import { t } from "../i18n"

const EMPLOYER_LINKS = [
  { to: "/employer/jobs", label: t.menu.myJobs },
  { to: "/employer/jobs/new", label: t.menu.newJob },
]

const CANDIDATE_LINKS = [
  { to: "/candidate/jobs", label: t.menu.jobs },
  { to: "/candidate/resume", label: t.menu.myResume },
]

export default function Layout({ children }) {
  const navigate = useNavigate()
  const role = localStorage.getItem("role")
  const links = role === "employer" ? EMPLOYER_LINKS : CANDIDATE_LINKS
  const home = role === "employer" ? "/employer/jobs" : "/candidate/jobs"

  function logout() {
    clearToken()
    localStorage.removeItem("role")
    navigate("/login")
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="border-b border-slate-800 bg-slate-950">
        <div className="mx-auto flex max-w-3xl items-center gap-6 px-8 py-4">
          <Link to={home} className="font-bold text-white">
            {t.menu.brand}
          </Link>

          <nav className="flex flex-1 gap-4">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="text-sm text-slate-300 hover:text-white"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <button
            type="button"
            onClick={logout}
            className="text-sm text-slate-400 hover:text-white"
          >
            {t.menu.logout}
          </button>
        </div>
      </header>

      <main>{children}</main>
    </div>
  )
}