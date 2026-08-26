import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"

import { get, post, put } from "../../api/client"
import { t } from "../../i18n"

export default function QuestionManage() {
  const { jobId } = useParams()

  const [questions, setQuestions] = useState([])
  const [checkedIds, setCheckedIds] = useState([])

  const [generating, setGenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)

  function load(data) {
    setQuestions(data)
    setCheckedIds(data.filter((item) => item.is_selected).map((item) => item.id))
  }

  useEffect(() => {
    get(`/assessments/jobs/${jobId}/questions`)
      .then(load)
      .catch(() => setQuestions([]))
  }, [jobId])

  async function generate() {
    setGenerating(true)
    setMessage(null)
    setError(null)

    try {
      load(await post(`/assessments/jobs/${jobId}/questions`, {}))
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setGenerating(false)
    }
  }

  function toggle(questionId) {
    if (checkedIds.includes(questionId)) {
      setCheckedIds(checkedIds.filter((id) => id !== questionId))
    } else {
      setCheckedIds([...checkedIds, questionId])
    }
  }

  async function saveSelection() {
    setSaving(true)
    setMessage(null)
    setError(null)

    try {
      load(await put(`/assessments/jobs/${jobId}/questions`, {
        question_ids: checkedIds,
      }))
      setMessage(t.questions.saved)
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <Link to="/employer/jobs" className="text-sm text-blue-400">
        {t.questions.back}
      </Link>

      <h1 className="mb-6 mt-2 text-2xl font-bold text-white">
        {t.questions.title}
      </h1>

      {error && <p className="mb-4 text-sm text-red-400">{error}</p>}
      {message && <p className="mb-4 text-sm text-green-400">{message}</p>}

      <div className="mb-4 flex items-center gap-3">
        <button
          type="button"
          onClick={generate}
          disabled={generating}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          {generating
            ? t.questions.generating
            : questions.length > 0
              ? t.questions.regenerate
              : t.questions.generate}
        </button>

        {questions.length > 0 && (
          <span className="text-sm text-slate-400">
            {checkedIds.length} {t.questions.selectedCount}
          </span>
        )}
      </div>

      {questions.length === 0 && !generating && (
        <p className="text-slate-400">{t.questions.noQuestions}</p>
      )}

      {questions.length > 0 && (
        <>
          <p className="mb-2 text-sm text-slate-300">{t.questions.selectHint}</p>

          <div className="space-y-2">
            {questions.map((question) => (
              <label
                key={question.id}
                className="flex cursor-pointer items-start gap-3 rounded bg-slate-800 p-3"
              >
                <input
                  type="checkbox"
                  checked={checkedIds.includes(question.id)}
                  onChange={() => toggle(question.id)}
                  className="mt-1"
                />
                <span className="text-sm text-slate-200">
                  {question.question_text}
                </span>
              </label>
            ))}
          </div>

          <button
            type="button"
            onClick={saveSelection}
            disabled={saving}
            className="mt-4 rounded bg-blue-600 px-6 py-2 font-medium text-white disabled:opacity-50"
          >
            {saving ? t.common.saving : t.questions.save}
          </button>
        </>
      )}
    </div>
  )
}