import { useEffect, useState } from "react"

import { get, post, put, upload } from "../../api/client"
import SkillSelect from "../../components/SkillSelect"
import { t, EDUCATION_LEVELS, FIELDS } from "../../i18n"

const inputClass =
  "w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"

export default function ResumeForm() {
  const [exists, setExists] = useState(false)
  const [phone, setPhone] = useState("")
  const [skillIds, setSkillIds] = useState([])
  const [experienceYears, setExperienceYears] = useState(0)
  const [educationLevel, setEducationLevel] = useState("bachelor")
  const [university, setUniversity] = useState("")
  const [field, setField] = useState("software_development")
  const [projects, setProjects] = useState("")
  const [certifications, setCertifications] = useState("")

  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [parsing, setParsing] = useState(false)
  const [unmatched, setUnmatched] = useState([])

  useEffect(() => {
    get("/resumes/me")
      .then((data) => {
        setExists(true)
        setPhone(data.phone || "")
        setSkillIds((data.skills || []).map((item) => item.skill_id))
        setExperienceYears(data.experience_years || 0)
        setEducationLevel(data.education_level || "bachelor")
        setUniversity(data.university || "")
        setField(data.field || "software_development")
        setProjects(data.projects || "")
        setCertifications(data.certifications || "")
      })
      .catch(() => setExists(false))
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

      if (data.phone) setPhone(data.phone)
      if (data.skill_ids.length) setSkillIds(data.skill_ids)
      if (data.experience_years) setExperienceYears(data.experience_years)
      if (data.education_level) setEducationLevel(data.education_level)
      if (data.university) setUniversity(data.university)
      if (data.field) setField(data.field)
      if (data.projects) setProjects(data.projects)
      if (data.certifications) setCertifications(data.certifications)

      setUnmatched(data.unmatched_skills || [])
      setMessage(t.resume.uploaded)
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
      university,
      field,
      projects,
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
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">{t.resume.title}</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <p className="text-sm text-red-400">{error}</p>}
        {message && <p className="text-sm text-green-400">{message}</p>}

        <div className="rounded bg-slate-800 p-3">
          <label className="block text-sm text-slate-300">
            {parsing ? t.resume.uploading : t.resume.upload}
            <input
              type="file"
              accept="application/pdf"
              onChange={handleUpload}
              disabled={parsing}
              className="mt-2 block w-full text-sm text-slate-400 file:mr-3 file:rounded file:border-0 file:bg-blue-600 file:px-3 file:py-1 file:text-sm file:text-white"
            />
          </label>

          {unmatched.length > 0 && (
            <p className="mt-2 text-xs text-amber-400">
              {t.resume.unmatched} {unmatched.join(", ")}
            </p>
          )}
        </div>

        <input
          type="text"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder={t.resume.phone}
          className={inputClass}
        />

        <div>
          <p className="mb-2 text-sm text-slate-300">{t.resume.skills}</p>
          <SkillSelect selected={skillIds} onChange={setSkillIds} />
        </div>

        <input
          type="number"
          min="0"
          value={experienceYears}
          onChange={(e) => setExperienceYears(e.target.value)}
          placeholder={t.resume.experienceYears}
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

        <input
          type="text"
          value={university}
          onChange={(e) => setUniversity(e.target.value)}
          placeholder={t.resume.university}
          className={inputClass}
        />

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

        <textarea
          value={projects}
          onChange={(e) => setProjects(e.target.value)}
          placeholder={t.resume.projects}
          rows="3"
          className={inputClass}
        />

        <textarea
          value={certifications}
          onChange={(e) => setCertifications(e.target.value)}
          placeholder={t.resume.certifications}
          rows="2"
          className={inputClass}
        />

        <button
          type="submit"
          disabled={loading}
          className="rounded bg-blue-600 px-6 py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? t.common.saving : t.common.save}
        </button>
      </form>
    </div>
  )
}