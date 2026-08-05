import { useEffect, useState } from "react"

import { get } from "../api/client"
import { t } from "../i18n"

export default function SkillSelect({ selected, onChange }) {
  const [categories, setCategories] = useState([])

  useEffect(() => {
    get("/skills").then(setCategories).catch(() => setCategories([]))
  }, [])

  function toggle(skill) {
    if (selected.includes(skill)) {
      onChange(selected.filter((item) => item !== skill))
    } else {
      onChange([...selected, skill])
    }
  }

  return (
    <div className="max-h-64 space-y-3 overflow-y-auto rounded bg-slate-700 p-3">
      {categories.map((category) => (
        <div key={category.key}>
          <p className="mb-1 text-xs font-medium text-slate-400">
            {t.skillCategories[category.key]}
          </p>
          <div className="flex flex-wrap gap-1">
            {category.skills.map((skill) => (
              <button
                key={skill}
                type="button"
                onClick={() => toggle(skill)}
                className={
                  selected.includes(skill)
                    ? "rounded bg-blue-600 px-2 py-1 text-xs text-white"
                    : "rounded bg-slate-600 px-2 py-1 text-xs text-slate-200"
                }
              >
                {skill}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}