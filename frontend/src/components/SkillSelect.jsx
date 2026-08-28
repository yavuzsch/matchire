import { useEffect, useMemo, useState } from "react"

import { get } from "../api/client"
import { t } from "../i18n"

export default function SkillSelect({ selected, onChange }) {
  const [groups, setGroups] = useState([])
  const [query, setQuery] = useState("")

  useEffect(() => {
    get("/skills").then(setGroups).catch(() => setGroups([]))
  }, [])

  const byId = useMemo(() => {
    const map = {}
    groups.forEach((group) => {
      group.skills.forEach((skill) => {
        map[skill.id] = skill.name
      })
    })
    return map
  }, [groups])

  function toggle(id) {
    const next = selected.includes(id)
      ? selected.filter((item) => item !== id)
      : [...selected, id]

    onChange(next, byId)
  }

  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase()

    if (!term) {
      return groups
    }

    return groups
      .map((group) => ({
        ...group,
        skills: group.skills.filter((skill) =>
          skill.name.toLowerCase().includes(term)
        ),
      }))
      .filter((group) => group.skills.length > 0)
  }, [groups, query])

  return (
    <div className="space-y-2">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={t.skills.search}
        className="w-full rounded bg-slate-700 px-3 py-2 text-sm text-white placeholder-slate-400"
      />

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
        {filtered.length === 0 && (
          <p className="text-xs text-slate-400">{t.skills.noResults}</p>
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