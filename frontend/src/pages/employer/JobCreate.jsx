import { useState } from "react"

import { post } from "../../api/client"
import SkillSelect from "../../components/SkillSelect"
import { t, EDUCATION_LEVELS, FIELDS } from "../../i18n"

const inputClass =
  "w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"

const REQUIREMENTS = ["mandatory", "required", "optional"]
const WEIGHTS = [1, 2, 3]

export default function JobCreate() {
  const [title, setTitle] = useState("")
  const [companyName, setCompanyName] = useState("")
  const [location, setLocation] = useState("")
  const [description, setDescription] = useState("")

  const [skillIds, setSkillIds] = useState([])
  const [skillNames, setSkillNames] = useState({})
  const [settings, setSettings] = useState({})

  const [experienceYears, setExperienceYears] = useState(0)
  const [assessmentSlots, setAssessmentSlots] = useState(5)
  const [assessmentWeight, setAssessmentWeight] = useState(50)
  const [educationLevel, setEducationLevel] = useState("bachelor")
  const [field, setField] = useState("software_development")

  const [rawText, setRawText] = useState("")
  const [parsing, setParsing] = useState(false)
  const [unmatched, setUnmatched] = useState([])

  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  function handleSkillsChange(ids, names) {
    setSkillIds(ids)
    setSkillNames(names)

    const next = {}
    ids.forEach((id) => {
      next[id] = settings[id] || { requirement: "required", weight: 2 }
    })
    setSettings(next)
  }

  function updateSetting(id, key, value) {
    setSettings({
      ...settings,
      [id]: { ...settings[id], [key]: value },
    })
  }

  async function handleParse() {
    if (!rawText.trim()) {
      return
    }

    setError(null)
    setMessage(null)
    setUnmatched([])
    setParsing(true)

    try {
      const data = await post("/jobs/parse", { text: rawText })

      if (data.title) setTitle(data.title)
      if (data.company_name) setCompanyName(data.company_name)
      if (data.location) setLocation(data.location)
      if (data.description) setDescription(data.description)
      if (data.experience_years) setExperienceYears(data.experience_years)
      if (data.education_level) setEducationLevel(data.education_level)
      if (data.field) setField(data.field)

      if (data.skills.length) {
        const ids = data.skills.map((item) => item.skill_id)
        const names = {}
        const next = {}

        data.skills.forEach((item) => {
          names[item.skill_id] = item.name
          next[item.skill_id] = {
            requirement: item.requirement,
            weight: item.weight,
          }
        })

        setSkillIds(ids)
        setSkillNames(names)
        setSettings(next)
      }

      setUnmatched(data.unmatched_skills || [])
      setMessage(t.job.parsed)
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setParsing(false)
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setMessage(null)
    setLoading(true)

    try {
      await post("/jobs", {
        title,
        company_name: companyName,
        location,
        description,
        description_raw: rawText.trim() || null,
        skills: skillIds.map((id) => ({
          skill_id: id,
          requirement: settings[id]?.requirement || "required",
          weight: settings[id]?.weight || 2,
        })),
        experience_years: Number(experienceYears),
        education_level: educationLevel,
        field,
        assessment_slots: Number(assessmentSlots),
        assessment_weight: Number(assessmentWeight),
      })
      setMessage(t.job.created)
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">{t.job.title}</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <p className="text-sm text-red-400">{error}</p>}
        {message && <p className="text-sm text-green-400">{message}</p>}

        <div className="space-y-2 rounded bg-slate-800 p-3">
          <p className="text-sm text-slate-300">{t.job.rawTextHint}</p>

          <textarea
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            placeholder={t.job.rawText}
            rows="5"
            className={inputClass}
          />

          <button
            type="button"
            onClick={handleParse}
            disabled={parsing || !rawText.trim()}
            className="rounded bg-blue-600 px-4 py-1 text-sm text-white disabled:opacity-50"
          >
            {parsing ? t.job.parsing : t.job.parse}
          </button>

          {unmatched.length > 0 && (
            <p className="text-xs text-amber-400">
              {t.job.unmatched} {unmatched.join(", ")}
            </p>
          )}
        </div>

        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder={t.job.jobTitle}
          required
          className={inputClass}
        />

        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder={t.job.companyName}
          required
          className={inputClass}
        />

        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder={t.job.location}
          className={inputClass}
        />

        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder={t.job.description}
          rows="3"
          className={inputClass}
        />

        <div>
          <p className="mb-2 text-sm text-slate-300">{t.job.skills}</p>
          <SkillSelect selected={skillIds} onChange={handleSkillsChange} />
        </div>

        {skillIds.length > 0 && (
          <div className="space-y-2 rounded bg-slate-800 p-3">
            <p className="text-sm text-slate-300">{t.job.skillsHint}</p>

            {skillIds.map((id) => (
              <div key={id} className="flex items-center gap-3">
                <span className="w-40 truncate text-sm text-white">
                  {skillNames[id]}
                </span>

                <select
                  value={settings[id]?.requirement || "required"}
                  onChange={(e) =>
                    updateSetting(id, "requirement", e.target.value)
                  }
                  className="rounded bg-slate-700 px-2 py-1 text-sm text-white"
                >
                  {REQUIREMENTS.map((value) => (
                    <option key={value} value={value}>
                      {t.skills.requirement[value]}
                    </option>
                  ))}
                </select>

                {settings[id]?.requirement !== "optional" && (
                  <select
                    value={settings[id]?.weight || 2}
                    onChange={(e) =>
                      updateSetting(id, "weight", Number(e.target.value))
                    }
                    className="rounded bg-slate-700 px-2 py-1 text-sm text-white"
                  >
                    {WEIGHTS.map((value) => (
                      <option key={value} value={value}>
                        {t.skills.weight[value]}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            ))}
          </div>
        )}

        <input
          type="number"
          min="0"
          value={experienceYears}
          onChange={(e) => setExperienceYears(e.target.value)}
          placeholder={t.resume.experienceYears}
          className={inputClass}
        />

        <input
          type="number"
          min="1"
          value={assessmentSlots}
          onChange={(e) => setAssessmentSlots(e.target.value)}
          placeholder={t.job.assessmentSlots}
          className={inputClass}
        />

        <input
          type="number"
          min="20"
          max="80"
          value={assessmentWeight}
          onChange={(e) => setAssessmentWeight(e.target.value)}
          placeholder={t.job.assessmentWeight}
          className={inputClass}
        />

        <select
          value={educationLevel}
          onChange={(e) => setEducationLevel(e.target.value)}
          className={inputClass}
        >
          {EDUCATION_LEVELS.map((value) => (
            <option key={value} value={value}>
              {t.educationLevels[value]}
            </option>
          ))}
        </select>

        <select
          value={field}
          onChange={(e) => setField(e.target.value)}
          className={inputClass}
        >
          {FIELDS.map((value) => (
            <option key={value} value={value}>
              {t.fields[value]}
            </option>
          ))}
        </select>

        <button
          type="submit"
          disabled={loading}
          className="rounded bg-blue-600 px-6 py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? t.job.submitting : t.job.submit}
        </button>
      </form>
    </div>
  )
}