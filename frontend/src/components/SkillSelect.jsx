import { useEffect, useMemo, useState } from "react"

import { get, post } from "../api/client"
import { t } from "../i18n"

export default function SkillSelect({ selected, onChange, names = {} }) {
  const [groups, setGroups] = useState([])
  const [extra, setExtra] = useState([])
  const [query, setQuery] = useState("")
  const [proposing, setProposing] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    get("/skills").then(setGroups).catch(() => setGroups([]))
  }, [])

  const byId = useMemo(() => {
    const map = { ...names }

    groups.forEach((group) => {
      group.skills.forEach((skill) => {
        map[skill.id] = skill.name
      })
    })

    extra.forEach((skill) => {
      map[skill.id] = skill.name
    })

    return map
  }, [groups, extra, names])

  function toggle(id) {
    const next = selected.includes(id)
      ? selected.filter((item) => item !== id)
      : [...selected, id]

    onChange(next, byId)
  }

  const term = query.trim()

  const filtered = useMemo(() => {
    const lowered = term.toLowerCase()

    if (!lowered) {
      return groups
    }

    return groups
      .map((group) => ({
        ...group,
        skills: group.skills.filter((skill) =>
          skill.name.toLowerCase().includes(lowered)
        ),
      }))
      .filter((group) => group.skills.length > 0)
  }, [groups, term])

  const hasResults = filtered.length > 0

  const hasExactMatch = useMemo(() => {
    const lowered = term.toLowerCase()

    if (!lowered) {
      return true
    }

    return filtered.some((group) =>
      group.skills.some((skill) => skill.name.toLowerCase() === lowered)
    )
  }, [filtered, term])

  async function propose() {
    setError(null)
    setProposing(true)

    try {
      const skill = await post("/skills/propose", { term })

      setExtra([...extra.filter((item) => item.id !== skill.id), skill])
      onChange([...selected.filter((id) => id !== skill.id), skill.id], {
        ...byId,
        [skill.id]: skill.name,
      })
      setQuery("")
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setProposing(false)
    }
  }

  return (
    <div className="space-y-2">
      <input
        type="text"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value)
          setError(null)
        }}
        placeholder={t.skills.search}
        className="w-full rounded bg-slate-700 px-3 py-2 text-sm text-white placeholder-slate-400"
      />

      {error && <p className="text-xs text-red-400">{error}</p>}

      {selected.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selected.map((id) => (
            <button
              key={id}
              type="button"
              onClick={() => toggle(id)}
              className="rounded bg-blue-600 px-2 py-1 text-xs text-white"
            >
              {byId[id] || id} ×
            </button>
          ))}
        </div>
      )}

      <div className="max-h-64 space-y-3 overflow-y-auto rounded bg-slate-700 p-3">
        {!hasResults && (
          <p className="text-xs text-slate-400">{t.skills.noResults}</p>
        )}

        {term.length > 1 && !hasExactMatch && (
          <div>
            <button
              type="button"
              onClick={propose}
              disabled={proposing}
              className="rounded bg-blue-600 px-3 py-1 text-xs text-white disabled:opacity-50"
            >
              {proposing ? t.skills.proposing : `${t.skills.propose}: ${term}`}
            </button>
          </div>
        )}

        {filtered.map((group) => (
          <div key={group.key}>
            <p className="mb-1 text-xs font-medium text-slate-400">
              {group.label}
            </p>
            <div className="flex flex-wrap gap-1">
              {group.skills.map((skill) => (
                <button
                  key={skill.id}
                  type="button"
                  onClick={() => toggle(skill.id)}
                  className={
                    selected.includes(skill.id)
                      ? "rounded bg-blue-600 px-2 py-1 text-xs text-white"
                      : "rounded bg-slate-600 px-2 py-1 text-xs text-slate-200"
                  }
                >
                  {skill.name}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}