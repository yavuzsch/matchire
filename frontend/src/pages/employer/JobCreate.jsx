import { useState } from "react"

import { post } from "../../api/client"
import SkillSelect from "../../components/SkillSelect"
import { t, EDUCATION_LEVELS, FIELDS } from "../../i18n"

const inputClass =
  "w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"

export default function JobCreate() {
  const [title, setTitle] = useState("")
  const [companyName, setCompanyName] = useState("")
  const [location, setLocation] = useState("")
  const [description, setDescription] = useState("")

  const [requiredSkills, setRequiredSkills] = useState([])
  const [mandatorySkills, setMandatorySkills] = useState([])
  const [skillWeights, setSkillWeights] = useState({})
  const [optionalSkills, setOptionalSkills] = useState([])

  const [experienceYears, setExperienceYears] = useState(0)
  const [interviewSlots, setInterviewSlots] = useState(5)
  const [educationLevel, setEducationLevel] = useState("bachelor")
  const [field, setField] = useState("software_development")

  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  function handleSkillsChange(skills) {
    setRequiredSkills(skills)

    const weights = {}
    skills.forEach((skill) => {
      weights[skill] = skillWeights[skill] || 1
    })
    setSkillWeights(weights)

    setMandatorySkills(mandatorySkills.filter((skill) => skills.includes(skill)))
    setOptionalSkills(optionalSkills.filter((skill) => !skills.includes(skill)))
  }

  function setWeight(skill, weight) {
    setSkillWeights({ ...skillWeights, [skill]: Number(weight) })
  }

  function toggleMandatory(skill) {
    if (mandatorySkills.includes(skill)) {
      setMandatorySkills(mandatorySkills.filter((item) => item !== skill))
    } else {
      setMandatorySkills([...mandatorySkills, skill])
    }
  }

  function handleOptionalChange(skills) {
    setOptionalSkills(skills.filter((skill) => !requiredSkills.includes(skill)))
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
        required_skills: requiredSkills,
        mandatory_skills: mandatorySkills,
        optional_skills: optionalSkills,
        skill_weights: skillWeights,
        experience_years: Number(experienceYears),
        education_level: educationLevel,
        field,
        interview_slots: Number(interviewSlots),
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
          <p className="mb-2 text-sm text-slate-300">{t.job.requiredSkills}</p>
          <SkillSelect selected={requiredSkills} onChange={handleSkillsChange} />
        </div>

        {requiredSkills.length > 0 && (
          <div className="space-y-2 rounded bg-slate-800 p-3">
            <p className="text-sm text-slate-300">{t.job.weightAndMandatory}</p>
            {requiredSkills.map((skill) => (
              <div key={skill} className="flex items-center gap-3">
                <span className="w-40 text-sm text-white">{skill}</span>

                <select
                  value={skillWeights[skill] || 1}
                  onChange={(e) => setWeight(skill, e.target.value)}
                  className="rounded bg-slate-700 px-2 py-1 text-sm text-white"
                >
                  <option value="1">{t.job.weightLow}</option>
                  <option value="2">{t.job.weightMedium}</option>
                  <option value="3">{t.job.weightHigh}</option>
                </select>

                <label className="flex items-center gap-1 text-sm text-slate-300">
                  <input
                    type="checkbox"
                    checked={mandatorySkills.includes(skill)}
                    onChange={() => toggleMandatory(skill)}
                  />
                  {t.job.mandatory}
                </label>
              </div>
            ))}
          </div>
        )}

        <div>
          <p className="mb-2 text-sm text-slate-300">{t.job.optionalSkills}</p>
          <SkillSelect selected={optionalSkills} onChange={handleOptionalChange} />
        </div>

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
          value={interviewSlots}
          onChange={(e) => setInterviewSlots(e.target.value)}
          placeholder={t.job.interviewSlots}
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