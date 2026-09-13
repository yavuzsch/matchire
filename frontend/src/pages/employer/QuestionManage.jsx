import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"

import { get, patch, post, put } from "../../api/client"
import Message from "../../components/Message"
import Spinner from "../../components/Spinner"
import { t } from "../../i18n"

export default function QuestionManage() {
  const { jobId } = useParams()

  const [questions, setQuestions] = useState([])
  const [checkedIds, setCheckedIds] = useState([])

  const [timeLimit, setTimeLimit] = useState("")
  const [savingTimeLimit, setSavingTimeLimit] = useState(false)

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

    get(`/jobs/${jobId}`)
      .then((job) => {
        if (job.assessment_time_limit_minutes) {
          setTimeLimit(String(job.assessment_time_limit_minutes))
        }
      })
      .catch(() => {})
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

  async function saveTimeLimit() {
    setSavingTimeLimit(true)
    setMessage(null)
    setError(null)

    try {
      await patch(`/jobs/${jobId}/settings`, {
        assessment_time_limit_minutes: timeLimit ? Number(timeLimit) : null,
      })
      setMessage(t.questions.timeLimitSaved)
    } catch (err) {
      setError(t.errors[err.code] || t.errors.UNKNOWN_ERROR)
    } finally {
      setSavingTimeLimit(false)
    }
  }

  return (
    <div>
      <Link to="/employer/jobs" className="text-sm font-medium text-blue-400 hover:text-blue-500">
        ← {t.questions.back}
      </Link>

      <h1 className="mt-2 text-2xl font-extrabold text-ink">
        {t.questions.title}
      </h1>

      <Message error={error} info={message} className="mt-4" />

      <div className="mt-6 flex items-end gap-3 rounded-xl bg-surface p-4">
        <div className="flex-1">
          <label className="mb-2 block text-sm font-medium text-ink">
            {t.questions.timeLimit}
          </label>
          <input
            type="number"
            min="5"
            max="180"
            value={timeLimit}
            onChange={(e) => setTimeLimit(e.target.value)}
            placeholder={t.questions.timeLimitPlaceholder}
            className="w-full rounded-lg bg-surface-2 px-3 py-2 text-sm text-ink placeholder-ink-soft outline-none ring-blue-500 focus:ring-2"
          />
        </div>

        <button
          type="button"
          onClick={saveTimeLimit}
          disabled={savingTimeLimit}
          className="flex items-center gap-2 rounded-lg bg-surface-2 px-4 py-2 text-sm font-semibold text-ink transition-colors hover:bg-surface disabled:opacity-50"
        >
          {savingTimeLimit && <Spinner />}
          {savingTimeLimit ? t.common.saving : t.common.save}
        </button>
      </div>

      <div className="mt-6 flex items-center gap-3">
        <button
          type="button"
          onClick={generate}
          disabled={generating}
          className="flex items-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
        >
          {generating && <Spinner />}
          {generating
            ? t.questions.generating
            : questions.length > 0
              ? t.questions.regenerate
              : t.questions.generate}
        </button>

        {questions.length > 0 && (
          <span className="text-sm text-ink-soft">
            {checkedIds.length} {t.questions.selectedCount}
          </span>
        )}
      </div>

      {questions.length === 0 && !generating && (
        <p className="mt-6 text-sm text-ink-soft">{t.questions.noQuestions}</p>
      )}

      {questions.length > 0 && (
        <>
          <p className="mt-6 text-sm text-ink-soft">{t.questions.selectHint}</p>

          <div className="mt-3 space-y-2">
            {questions.map((question) => (
              <label
                key={question.id}
                className="flex cursor-pointer items-start gap-3 rounded-xl bg-surface p-4"
              >
                <input
                  type="checkbox"
                  checked={checkedIds.includes(question.id)}
                  onChange={() => toggle(question.id)}
                  className="mt-1"
                />
                <span className="text-sm text-ink">
                  {question.question_text}
                </span>
              </label>
            ))}
          </div>

          <button
            type="button"
            onClick={saveSelection}
            disabled={saving}
            className="mt-6 flex items-center gap-2 rounded-lg bg-blue-500 px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
          >
            {saving && <Spinner />}
            {saving ? t.common.saving : t.questions.save}
          </button>
        </>
      )}
    </div>
  )
}