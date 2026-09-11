export default function Message({ error, info, className = "" }) {
  if (!error && !info) {
    return null
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {error && (
        <p className="rounded-lg bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </p>
      )}
      {info && (
        <p className="rounded-lg bg-green-500/10 px-4 py-3 text-sm text-green-400">
          {info}
        </p>
      )}
    </div>
  )
}