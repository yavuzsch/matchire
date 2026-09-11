import { Link } from "react-router-dom"

import LanguageToggle from "../components/LanguageToggle"
import { t } from "../i18n"

const SIDE_A_STEPS = [t.home.sideAStep1, t.home.sideAStep2, t.home.sideAStep3]
const SIDE_B_STEPS = [t.home.sideBStep1, t.home.sideBStep2, t.home.sideBStep3]

export default function Home() {
  return (
    <div className="min-h-screen bg-base">
      <header className="border-b border-line bg-surface">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <span className="text-lg font-extrabold text-ink">{t.menu.brand}</span>

          <div className="flex items-center gap-4">
            <LanguageToggle />

            <Link to="/login" className="text-sm font-medium text-ink-soft hover:text-ink">
              {t.home.login}
            </Link>
            <Link
              to="/register"
              className="rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-600"
            >
              {t.home.register}
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto flex max-w-5xl flex-col items-center gap-14 px-6 py-20 lg:flex-row">
        <div className="flex-1 text-center lg:text-left">
          <h1 className="text-4xl font-extrabold leading-tight text-ink lg:text-5xl">
            {t.home.heroTitle}
          </h1>
          <p className="mx-auto mt-4 max-w-md text-lg text-ink-soft lg:mx-0">
            {t.home.heroDescription}
          </p>

          <div className="mt-8 flex justify-center gap-3 lg:justify-start">
            <Link
              to="/register"
              className="rounded-lg bg-blue-500 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-600"
            >
              {t.home.getStarted}
            </Link>
            <Link
              to="/login"
              className="rounded-lg bg-surface-2 px-6 py-3 text-sm font-semibold text-ink hover:bg-surface"
            >
              {t.home.login}
            </Link>
          </div>
        </div>

        <div className="w-full max-w-xs flex-1">
          <MatchCard />
        </div>
      </section>

      <section className="border-t border-line bg-surface">
        <div className="mx-auto max-w-5xl px-6 py-16">
          <div className="grid gap-12 sm:grid-cols-2">
            <div>
              <h2 className="text-xl font-extrabold text-ink">
                {t.home.sideATitle}
              </h2>
              <ol className="mt-5 space-y-4">
                {SIDE_A_STEPS.map((step, i) => (
                  <li key={i} className="flex gap-3 text-sm text-ink-soft">
                    <span className="font-mono text-blue-400">{i + 1}</span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>

            <div>
              <h2 className="text-xl font-extrabold text-ink">
                {t.home.sideBTitle}
              </h2>
              <ol className="mt-5 space-y-4">
                {SIDE_B_STEPS.map((step, i) => (
                  <li key={i} className="flex gap-3 text-sm text-ink-soft">
                    <span className="font-mono text-blue-400">{i + 1}</span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

function MatchCard() {
  return (
    <div className="rounded-xl bg-surface p-6 shadow-xl shadow-black/20">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-semibold text-ink">Backend Developer</p>
          <p className="text-xs text-ink-soft">ABC Holding · İstanbul</p>
        </div>
        <span className="font-mono text-lg font-bold text-green-400">92%</span>
      </div>

      <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-surface-2">
        <span className="block h-full w-[92%] rounded-full bg-green-400" />
      </div>

      <p className="mt-4 text-xs text-ink-soft">3 yıl deneyim · Lisans</p>
    </div>
  )
}