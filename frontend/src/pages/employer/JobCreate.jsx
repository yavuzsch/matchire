import { useState } from "react"

import { post } from "../../api/client"
import { Field, inputClass, Section } from "../../components/FormElements"
import Message from "../../components/Message"
import SkillSelect from "../../components/SkillSelect"
import Spinner from "../../components/Spinner"
import { t, EDUCATION_LEVELS, FIELDS } from "../../i18n"

const selectClass =
  "rounded-lg bg-surface-2 px-2 py-1.5 text-sm text-ink outline-none ring-blue-500 focus:ring-2"

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
    <div className="max-w-2xl">
      <h1 className="text-2xl font-extrabold text-ink">{t.job.title}</h1>

      <form onSubmit={handleSubmit} className="mt-6 space-y-6">
        <Message error={error} info={message} />

        <Section title={t.job.autofillTitle}>
          <Field label={t.job.rawText} hint={t.job.rawTextHint}>
            <textarea
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              rows="5"
              className={inputClass}
            />
          </Field>

          <button
            type="button"
            onClick={handleParse}
            disabled={parsing || !rawText.trim()}
            className="flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
          >
            {parsing && <Spinner />}
            {parsing ? t.job.parsing : t.job.parse}
          </button>

          {unmatched.length > 0 && (
            <p className="text-xs text-blue-400">
              {t.job.unmatched} {unmatched.join(", ")}
            </p>
          )}
        </Section>

        <Section title={t.job.basicInfoTitle}>
          <Field label={t.job.jobTitle}>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className={inputClass}
            />
          </Field>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label={t.job.companyName}>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                required
                className={inputClass}
              />
            </Field>

            <Field label={t.job.location}>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className={inputClass}
              />
            </Field>
          </div>

          <Field label={t.job.description}>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows="3"
              className={inputClass}
            />
          </Field>
        </Section>

        <Section title={t.job.requirementsTitle}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label={t.resume.experienceYears}>
              <input
                type="number"
                min="0"
                value={experienceYears}
                onChange={(e) => setExperienceYears(e.target.value)}
                className={inputClass}
              />
            </Field>

            <Field label={t.job.educationLevelLabel}>
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
            </Field>
          </div>

          <Field label={t.job.fieldLabel}>
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
          </Field>
        </Section>

        <Section title={t.job.skills}>
          <SkillSelect selected={skillIds} onChange={handleSkillsChange} />

          {skillIds.length > 0 && (
            <div className="space-y-3 border-t border-line pt-4">
              <p className="text-xs text-ink-soft">{t.job.skillsHint}</p>

              {skillIds.map((id) => (
                <div key={id} className="flex items-center gap-3">
                  <span className="w-40 truncate text-sm text-ink">
                    {skillNames[id]}
                  </span>

                  <select
                    value={settings[id]?.requirement || "required"}
                    onChange={(e) =>
                      updateSetting(id, "requirement", e.target.value)
                    }
                    className={selectClass}
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
                      className={selectClass}
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
        </Section>

        <Section title={t.job.assessmentSettingsTitle}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label={t.job.assessmentSlots}>
              <input
                type="number"
                min="1"
                value={assessmentSlots}
                onChange={(e) => setAssessmentSlots(e.target.value)}
                className={inputClass}
              />
            </Field>

            <Field label={t.job.assessmentWeight}>
              <input
                type="number"
                min="20"
                max="80"
                value={assessmentWeight}
                onChange={(e) => setAssessmentWeight(e.target.value)}
                className={inputClass}
              />
            </Field>
          </div>
        </Section>

        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-500 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
        >
          {loading && <Spinner />}
          {loading ? t.job.submitting : t.job.submit}
        </button>
      </form>
    </div>
  )
}