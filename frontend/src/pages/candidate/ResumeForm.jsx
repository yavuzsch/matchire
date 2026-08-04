import { useEffect, useState } from "react"

import { get, post, put } from "../../api/client"
import SkillSelect from "../../components/SkillSelect"

const EDUCATION_LEVELS = [
  { value: "high_school", label: "Lise" },
  { value: "associate", label: "Ön Lisans" },
  { value: "bachelor", label: "Lisans" },
  { value: "master", label: "Yüksek Lisans" },
  { value: "doctorate", label: "Doktora" },
]

const FIELDS = [
  { value: "software_development", label: "Yazılım Geliştirme" },
  { value: "data_science", label: "Veri Bilimi" },
  { value: "artificial_intelligence", label: "Yapay Zeka" },
  { value: "cyber_security", label: "Siber Güvenlik" },
  { value: "mobile_development", label: "Mobil Geliştirme" },
  { value: "data_engineering", label: "Veri Mühendisliği" },
  { value: "devops", label: "DevOps" },
  { value: "quality_assurance", label: "Test ve Kalite" },
]

const inputClass =
  "w-full rounded bg-slate-700 px-3 py-2 text-white placeholder-slate-400"

export default function ResumeForm() {
  const [exists, setExists] = useState(false)
  const [phone, setPhone] = useState("")
  const [skills, setSkills] = useState([])
  const [experienceYears, setExperienceYears] = useState(0)
  const [educationLevel, setEducationLevel] = useState("bachelor")
  const [university, setUniversity] = useState("")
  const [field, setField] = useState("software_development")
  const [projects, setProjects] = useState("")
  const [certifications, setCertifications] = useState("")

  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    get("/resumes/me")
      .then((data) => {
        setExists(true)
        setPhone(data.phone || "")
        setSkills(data.skills || [])
        setExperienceYears(data.experience_years || 0)
        setEducationLevel(data.education_level || "bachelor")
        setUniversity(data.university || "")
        setField(data.field || "software_development")
        setProjects(data.projects || "")
        setCertifications(data.certifications || "")
      })
      .catch(() => setExists(false))
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setMessage(null)
    setLoading(true)

    const body = {
      phone,
      skills,
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
      setMessage("Özgeçmiş kaydedildi")
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">Özgeçmişim</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <p className="text-sm text-red-400">{error}</p>}
        {message && <p className="text-sm text-green-400">{message}</p>}

        <input
          type="text"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="Telefon"
          className={inputClass}
        />

        <div>
          <p className="mb-2 text-sm text-slate-300">Beceriler</p>
          <SkillSelect selected={skills} onChange={setSkills} />
        </div>

        <input
          type="number"
          min="0"
          value={experienceYears}
          onChange={(e) => setExperienceYears(e.target.value)}
          placeholder="Deneyim (yıl)"
          className={inputClass}
        />

        <select
          value={educationLevel}
          onChange={(e) => setEducationLevel(e.target.value)}
          className={inputClass}
        >
          {EDUCATION_LEVELS.map((level) => (
            <option key={level.value} value={level.value}>
              {level.label}
            </option>
          ))}
        </select>

        <input
          type="text"
          value={university}
          onChange={(e) => setUniversity(e.target.value)}
          placeholder="Üniversite"
          className={inputClass}
        />

        <select
          value={field}
          onChange={(e) => setField(e.target.value)}
          className={inputClass}
        >
          {FIELDS.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>

        <textarea
          value={projects}
          onChange={(e) => setProjects(e.target.value)}
          placeholder="Projeler"
          rows="3"
          className={inputClass}
        />

        <textarea
          value={certifications}
          onChange={(e) => setCertifications(e.target.value)}
          placeholder="Sertifikalar"
          rows="2"
          className={inputClass}
        />

        <button
          type="submit"
          disabled={loading}
          className="rounded bg-blue-600 px-6 py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? "Kaydediliyor..." : "Kaydet"}
        </button>
      </form>
    </div>
  )
}