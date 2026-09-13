import { useEffect, useState } from "react"

import { get, post, put, upload } from "../../api/client"
import { Field, inputClass, Section } from "../../components/FormElements"
import Message from "../../components/Message"
import SkillSelect from "../../components/SkillSelect"
import Spinner from "../../components/Spinner"
import { t, EDUCATION_LEVELS, FIELDS } from "../../i18n"

const emptyResume = {
  phone: "",
  skillIds: [],
  skillNames: {},
  experienceYears: 0,
  educationLevel: "bachelor",
  school: "",
  field: "software_development",
  projects: "",
  projectSummary: "",
  certifications: "",
}

function fromServer(data) {
  const items = data.skills || []
  return {
    phone: data.phone || "",
    skillIds: items.map((item) => item.skill_id),
    skillNames: Object.fromEntries(items.map((item) => [item.skill_id, item.name])),
    experienceYears: data.experience_years || 0,
    educationLevel: data.education_level || "bachelor",
    school: data.university || "",
    field: data.field || "software_development",
    projects: data.projects || "",
    projectSummary: data.project_summary || "",
    certifications: data.certifications || "",
  }
}

export default function ResumeForm() {
  const [exists, setExists] = useState(false)
  const [editing, setEditing] = useState(false)
  const [saved, setSaved] = useState(emptyResume)
  const [draft, setDraft] = useState(emptyResume)

  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [parsing, setParsing] = useState(false)
  const [unmatched, setUnmatched] = useState([])

  const schoolLabel =
    draft.educationLevel === "high_school" ? t.resume.highSchool : t.resume.university

  useEffect(() => {
    get("/resumes/me")
      .then((data) => {
        const parsed = fromServer(data)
        setExists(true)
        setSaved(parsed)
        setDraft(parsed)
      })
      .catch(() => {
        setExists(false)
        setEditing(true)
      })
  }, [])

  function updateDraft(patch) {
    setDraft({ ...draft, ...patch })
  }

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

      const skillIds = data.skill_ids || []
      updateDraft({
        phone: data.phone || draft.phone,
        skillIds,
        skillNames: Object.fromEntries(
          skillIds.map((id, index) => [id, data.skill_names[index]])
        ),
        experienceYears: data.experience_years || draft.experienceYears,
        educationLevel: data.education_level || draft.educationLevel,
        school: data.university || draft.school,
        field: data.field || draft.field,
        projects: data.projects || draft.projects,
        projectSummary: data.project_summary || draft.projectSummary,
        certifications: data.certifications || draft.certifications,
      })

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
      phone: draft.phone,
      skill_ids: draft.skillIds,
      experience_years: Number(draft.experienceYears),
      education_level: draft.educationLevel,
      university: draft.school,
      field: draft.field,
      projects: draft.projects,
      project_summary: draft.projectSummary || null,
      certifications: draft.certifications,
      languages: {},
    }

    try {
      if (exists) {
        await put("/resumes/me", body)
      } else {
        await post("/resumes", body)
        setExists(true)
      }
      setSaved(draft)
      setMessage(t.resume.saved)
      setEditing(false)
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setLoading(false)
    }
  }

  function handleCancel() {
    setDraft(saved)
    setError(null)
    setMessage(null)
    setEditing(false)
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
            {saved.phone && (
              <div>
                <p className="text-xs text-ink-soft">{t.resume.phone}</p>
                <p className="mt-1 text-sm text-ink">{saved.phone}</p>
              </div>
            )}

            <div>
              <p className="text-xs text-ink-soft">{t.resume.skills}</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {saved.skillIds.length === 0 && (
                  <p className="text-sm text-ink-soft">—</p>
                )}
                {saved.skillIds.map((id) => (
                  <span
                    key={id}
                    className="rounded-full bg-surface-2 px-3 py-1 text-xs text-ink-soft"
                  >
                    {saved.skillNames[id]}
                  </span>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-ink-soft">{t.resume.experienceYears}</p>
                <p className="mt-1 text-sm text-ink">{saved.experienceYears}</p>
              </div>

              <div>
                <p className="text-xs text-ink-soft">{t.job.educationLevelLabel}</p>
                <p className="mt-1 text-sm text-ink">
                  {t.educationLevels[saved.educationLevel]}
                </p>
              </div>
            </div>

            {saved.school && (
              <div>
                <p className="text-xs text-ink-soft">
                  {saved.educationLevel === "high_school"
                    ? t.resume.highSchool
                    : t.resume.university}
                </p>
                <p className="mt-1 text-sm text-ink">{saved.school}</p>
              </div>
            )}

            <div>
              <p className="text-xs text-ink-soft">{t.job.fieldLabel}</p>
              <p className="mt-1 text-sm text-ink">{t.fields[saved.field]}</p>
            </div>

            {saved.projects && (
              <div>
                <p className="text-xs text-ink-soft">{t.resume.projects}</p>
                <p className="mt-1 whitespace-pre-line text-sm text-ink">{saved.projects}</p>
              </div>
            )}

            {saved.projectSummary && (
              <div>
                <p className="text-xs text-ink-soft">{t.resume.projectSummary}</p>
                <p className="mt-1 text-sm text-ink">{saved.projectSummary}</p>
              </div>
            )}

            {saved.certifications && (
              <div>
                <p className="text-xs text-ink-soft">{t.resume.certifications}</p>
                <p className="mt-1 whitespace-pre-line text-sm text-ink">
                  {saved.certifications}
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
              value={draft.phone}
              onChange={(e) => updateDraft({ phone: e.target.value })}
              className={inputClass}
            />
          </Field>
        </Section>

        <Section title={t.resume.skills}>
          <SkillSelect
            selected={draft.skillIds}
            onChange={(ids, names) => updateDraft({ skillIds: ids, skillNames: names })}
            names={draft.skillNames}
          />
        </Section>

        <Section title={t.resume.backgroundSectionTitle}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label={t.resume.experienceYears}>
              <input
                type="number"
                min="0"
                value={draft.experienceYears}
                onChange={(e) => updateDraft({ experienceYears: e.target.value })}
                className={inputClass}
              />
            </Field>

            <Field label={t.job.educationLevelLabel}>
              <select
                value={draft.educationLevel}
                onChange={(e) => updateDraft({ educationLevel: e.target.value })}
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
              value={draft.school}
              onChange={(e) => updateDraft({ school: e.target.value })}
              className={inputClass}
            />
          </Field>

          <Field label={t.job.fieldLabel}>
            <select
              value={draft.field}
              onChange={(e) => updateDraft({ field: e.target.value })}
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
              value={draft.projects}
              onChange={(e) => updateDraft({ projects: e.target.value })}
              rows="3"
              className={inputClass}
            />
          </Field>

          <Field label={t.resume.projectSummary}>
            <textarea
              value={draft.projectSummary}
              onChange={(e) => updateDraft({ projectSummary: e.target.value })}
              rows="2"
              className={inputClass}
            />
          </Field>

          <Field label={t.resume.certifications}>
            <textarea
              value={draft.certifications}
              onChange={(e) => updateDraft({ certifications: e.target.value })}
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
              onClick={handleCancel}
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