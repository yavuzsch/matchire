export const inputClass =
  "w-full rounded-lg bg-surface-2 px-3 py-2 text-sm text-ink placeholder-ink-soft outline-none ring-blue-500 focus:ring-2"

export const authInputClass =
  "w-full rounded-lg bg-surface-2 px-4 py-3 text-sm text-ink placeholder-ink-soft outline-none ring-blue-500 focus:ring-2"

export function Field({ label, hint, children }) {
  return (
    <div>
      <label className="text-sm font-medium text-ink">{label}</label>
      {hint && <p className="mt-0.5 text-xs text-ink-soft">{hint}</p>}
      <div className="mt-2">{children}</div>
    </div>
  )
}

export function Section({ title, children }) {
  return (
    <div className="rounded-xl bg-surface p-6">
      <h2 className="font-semibold text-ink">{title}</h2>
      <div className="mt-4 space-y-4">{children}</div>
    </div>
  )
}