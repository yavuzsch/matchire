export default function ScoreBadge({ label, value }) {
  const tone =
    value >= 70 ? "bg-green-900 text-green-300"
      : value >= 40 ? "bg-yellow-900 text-yellow-300"
        : "bg-slate-700 text-slate-300"

  return (
    <span className={`rounded px-2 py-1 text-xs ${tone}`}>
      {label}: {value}
    </span>
  )
}