import { Link, useNavigate } from "react-router-dom"

import { clearToken } from "../api/client"
import LanguageToggle from "./LanguageToggle"
import { t } from "../i18n"

const EMPLOYER_LINKS = [
  { to: "/employer/jobs", label: t.menu.myJobs },
  { to: "/employer/jobs/new", label: t.menu.newJob },
]

const CANDIDATE_LINKS = [
  { to: "/candidate/jobs", label: t.menu.jobs },
  { to: "/candidate/applications", label: t.menu.myApplications },
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
    <div className="min-h-screen bg-base">
      <header className="border-b border-line bg-surface">
        <div className="mx-auto flex max-w-3xl items-center gap-8 px-6 py-4">
          <Link to={home} className="text-lg font-extrabold text-ink">
            {t.menu.brand}
          </Link>

          <nav className="flex flex-1 gap-6">
            {links.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="text-sm font-medium text-ink-soft transition-colors hover:text-ink"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          <div className="flex shrink-0 items-center gap-4">
            <LanguageToggle />

            <Link
              to="/account"
              className="text-sm font-medium text-ink-soft transition-colors hover:text-ink"
            >
              {t.menu.myAccount}
            </Link>

            <button
              type="button"
              onClick={logout}
              className="rounded-lg bg-surface-2 px-3 py-1.5 text-sm font-medium text-ink-soft transition-colors hover:text-ink"
            >
              {t.menu.logout}
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-10">{children}</main>
    </div>
  )
}