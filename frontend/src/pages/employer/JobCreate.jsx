import { useState } from "react"

import { post } from "../../api/client"
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

export default function JobCreate() {
  const [title, setTitle] = useState("")
  const [companyName, setCompanyName] = useState("")
  const [location, setLocation] = useState("")
  const [description, setDescription] = useState("")

  const [requiredSkills, setRequiredSkills] = useState([])
  const [mandatorySkills, setMandatorySkills] = useState([])
  const [skillWeights, setSkillWeights] = useState({})

  const [experienceYears, setExperienceYears] = useState(0)
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
        optional_skills: [],
        skill_weights: skillWeights,
        experience_years: Number(experienceYears),
        education_level: educationLevel,
        field,
      })
      setMessage("İlan oluşturuldu")
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="mb-6 text-2xl font-bold text-white">Yeni İlan</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <p className="text-sm text-red-400">{error}</p>}
        {message && <p className="text-sm text-green-400">{message}</p>}

        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="İlan başlığı"
          required
          className={inputClass}
        />

        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="Şirket adı"
          required
          className={inputClass}
        />

        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Konum"
          className={inputClass}
        />

        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Pozisyon açıklaması"
          rows="3"
          className={inputClass}
        />

        <div>
          <p className="mb-2 text-sm text-slate-300">Aranan beceriler</p>
          <SkillSelect selected={requiredSkills} onChange={handleSkillsChange} />
        </div>

        {requiredSkills.length > 0 && (
          <div className="space-y-2 rounded bg-slate-800 p-3">
            <p className="text-sm text-slate-300">Önem derecesi ve zorunluluk</p>
            {requiredSkills.map((skill) => (
              <div key={skill} className="flex items-center gap-3">
                <span className="w-40 text-sm text-white">{skill}</span>

                <select
                  value={skillWeights[skill] || 1}
                  onChange={(e) => setWeight(skill, e.target.value)}
                  className="rounded bg-slate-700 px-2 py-1 text-sm text-white"
                >
                  <option value="1">Düşük</option>
                  <option value="2">Orta</option>
                  <option value="3">Yüksek</option>
                </select>

                <label className="flex items-center gap-1 text-sm text-slate-300">
                  <input
                    type="checkbox"
                    checked={mandatorySkills.includes(skill)}
                    onChange={() => toggleMandatory(skill)}
                  />
                  Zorunlu
                </label>
              </div>
            ))}
          </div>
        )}

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

        <button
          type="submit"
          disabled={loading}
          className="rounded bg-blue-600 px-6 py-2 font-medium text-white disabled:opacity-50"
        >
          {loading ? "Oluşturuluyor..." : "İlanı Oluştur"}
        </button>
      </form>
    </div>
  )
}