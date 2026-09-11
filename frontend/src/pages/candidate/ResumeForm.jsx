import { useEffect, useState } from "react"

import { get, post, put, upload } from "../../api/client"
import { Field, inputClass, Section } from "../../components/FormElements"
import Message from "../../components/Message"
import SkillSelect from "../../components/SkillSelect"
import Spinner from "../../components/Spinner"
import { t, EDUCATION_LEVELS, FIELDS } from "../../i18n"

export default function ResumeForm() {
  const [exists, setExists] = useState(false)
  const [editing, setEditing] = useState(false)

  const [phone, setPhone] = useState("")
  const [skillIds, setSkillIds] = useState([])
  const [skillNames, setSkillNames] = useState({})
  const [experienceYears, setExperienceYears] = useState(0)
  const [educationLevel, setEducationLevel] = useState("bachelor")
  const [school, setSchool] = useState("")
  const [field, setField] = useState("software_development")
  const [projects, setProjects] = useState("")
  const [projectSummary, setProjectSummary] = useState("")
  const [certifications, setCertifications] = useState("")

  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [parsing, setParsing] = useState(false)
  const [unmatched, setUnmatched] = useState([])

  const schoolLabel =
    educationLevel === "high_school" ? t.resume.highSchool : t.resume.university

  useEffect(() => {
    get("/resumes/me")
      .then((data) => {
        const items = data.skills || []

        setExists(true)
        setPhone(data.phone || "")
        setSkillIds(items.map((item) => item.skill_id))
        setSkillNames(
          Object.fromEntries(items.map((item) => [item.skill_id, item.name]))
        )
        setExperienceYears(data.experience_years || 0)
        setEducationLevel(data.education_level || "bachelor")
        setSchool(data.university || "")
        setField(data.field || "software_development")
        setProjects(data.projects || "")
        setProjectSummary(data.project_summary || "")
        setCertifications(data.certifications || "")
      })
      .catch(() => {
        setExists(false)
        setEditing(true)
      })
  }, [])

  async function handleUpload(event) {
    const file = event.target.files?.[0]
    if (!file) {
      return
    }

    setError(null)
    setMessage(null)
    setUnmatched([])
    setParsing(true)

    try {
      const data = await upload("/resumes/parse", file)

      setPhone(data.phone || "")

      setSkillIds(data.skill_ids || [])
      setSkillNames(
        Object.fromEntries(
          (data.skill_ids || []).map((id, index) => [id, data.skill_names[index]])
        )
      )

      setExperienceYears(data.experience_years || 0)
      setEducationLevel(data.education_level || "bachelor")
      setSchool(data.university || "")
      setField(data.field || "software_development")
      setProjects(data.projects || "")
      setProjectSummary(data.project_summary || "")
      setCertifications(data.certifications || "")

      setUnmatched(data.unmatched_skills || [])
      setMessage(t.resume.uploaded)
      setEditing(true)
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setParsing(false)
      event.target.value = ""
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setMessage(null)
    setLoading(true)

    const body = {
      phone,
      skill_ids: skillIds,
      experience_years: Number(experienceYears),
      education_level: educationLevel,
      university: school,
      field,
      projects,
      project_summary: projectSummary || null,
      certifications,
      languages: {},
    }

    try {
      if (exists) {
        await put("/resumes/me", body)
      } else {
        await post("/resumes", body)
        setExists(true)
      }
      setMessage(t.resume.saved)
      setEditing(false)
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setLoading(false)
    }
  }

  if (!editing) {
    return (
      <div className="max-w-2xl">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-extrabold text-ink">{t.resume.title}</h1>
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="rounded-lg bg-surface-2 px-4 py-2 text-sm font-semibold text-ink hover:bg-surface"
          >
            {t.common.edit}
          </button>
        </div>

        <Message info={message} className="mt-4" />

        <div className="mt-6 rounded-xl bg-surface p-6">
          <div className="space-y-5">
            {phone && (
              <div>
                <p className="text-xs text-ink-soft">{t.resume.phone}</p>
                <p className="mt-1 text-sm text-ink">{phone}</p>
              </div>
            )}

            <div>
              <p className="text-xs text-ink-soft">{t.resume.skills}</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {skillIds.length === 0 && (
                  <p className="text-sm text-ink-soft">—</p>
                )}
                {skillIds.map((id) => (
                  <span
                    key={id}
                    className="rounded-full bg-surface-2 px-3 py-1 text-xs text-ink-soft"
                  >
                    {skillNames[id]}
                  </span>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-ink-soft">{t.resume.experienceYears}</p>
                <p className="mt-1 text-sm text-ink">{experienceYears}</p>
              </div>

              <div>
                <p className="text-xs text-ink-soft">{t.job.educationLevelLabel}</p>
                <p className="mt-1 text-sm text-ink">
                  {t.educationLevels[educationLevel]}
                </p>
              </div>
            </div>

            {school && (
              <div>
                <p className="text-xs text-ink-soft">{schoolLabel}</p>
                <p className="mt-1 text-sm text-ink">{school}</p>
              </div>
            )}

            <div>
              <p className="text-xs text-ink-soft">{t.job.fieldLabel}</p>
              <p className="mt-1 text-sm text-ink">{t.fields[field]}</p>
            </div>

            {projects && (
              <div>
                <p className="text-xs text-ink-soft">{t.resume.projects}</p>
                <p className="mt-1 whitespace-pre-line text-sm text-ink">{projects}</p>
              </div>
            )}

            {projectSummary && (
              <div>
                <p className="text-xs text-ink-soft">{t.resume.projectSummary}</p>
                <p className="mt-1 text-sm text-ink">{projectSummary}</p>
              </div>
            )}

            {certifications && (
              <div>
                <p className="text-xs text-ink-soft">{t.resume.certifications}</p>
                <p className="mt-1 whitespace-pre-line text-sm text-ink">
                  {certifications}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-extrabold text-ink">{t.resume.title}</h1>

      <form onSubmit={handleSubmit} className="mt-6 space-y-6">
        <Message error={error} info={message} />

        <Section title={t.resume.uploadSectionTitle}>
          <label className="block text-sm text-ink-soft">
            <span className="flex items-center gap-2">
              {parsing && <Spinner />}
              {parsing ? t.resume.uploading : t.resume.upload}
            </span>
            <input
              type="file"
              accept="application/pdf"
              onChange={handleUpload}
              disabled={parsing}
              className="mt-2 block w-full text-sm text-ink-soft file:mr-3 file:rounded-lg file:border-0 file:bg-blue-500 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-white"
            />
          </label>

          {unmatched.length > 0 && (
            <p className="mt-2 text-xs text-blue-400">
              {t.resume.unmatched} {unmatched.join(", ")}
            </p>
          )}
        </Section>

        <Section title={t.resume.contactSectionTitle}>
          <Field label={t.resume.phone}>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className={inputClass}
            />
          </Field>
        </Section>

        <Section title={t.resume.skills}>
          <SkillSelect
            selected={skillIds}
            onChange={setSkillIds}
            names={skillNames}
          />
        </Section>

        <Section title={t.resume.backgroundSectionTitle}>
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

          <Field label={schoolLabel}>
            <input
              type="text"
              value={school}
              onChange={(e) => setSchool(e.target.value)}
              className={inputClass}
            />
          </Field>

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

        <Section title={t.resume.projectsSectionTitle}>
          <Field label={t.resume.projects}>
            <textarea
              value={projects}
              onChange={(e) => setProjects(e.target.value)}
              rows="3"
              className={inputClass}
            />
          </Field>

          <Field label={t.resume.projectSummary}>
            <textarea
              value={projectSummary}
              onChange={(e) => setProjectSummary(e.target.value)}
              rows="2"
              className={inputClass}
            />
          </Field>

          <Field label={t.resume.certifications}>
            <textarea
              value={certifications}
              onChange={(e) => setCertifications(e.target.value)}
              rows="2"
              className={inputClass}
            />
          </Field>
        </Section>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading}
            className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-blue-500 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
          >
            {loading && <Spinner />}
            {loading ? t.common.saving : t.common.save}
          </button>

          {exists && (
            <button
              type="button"
              onClick={() => setEditing(false)}
              className="rounded-lg bg-surface-2 px-6 py-3 text-sm font-semibold text-ink hover:bg-surface"
            >
              {t.common.cancel}
            </button>
          )}
        </div>
      </form>
    </div>
  )
}