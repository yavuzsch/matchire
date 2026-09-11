export default function ScoreBadge({ label, value }) {
  const tone =
    value >= 70
      ? "bg-green-500/10 text-green-400"
      : value >= 40
        ? "bg-blue-500/10 text-blue-400"
        : "bg-surface-2 text-ink-soft"

  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${tone}`}>
      {label}: {value}
    </span>
  )
}