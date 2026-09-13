import { useEffect, useState } from "react"

const NODES = [
  { x: 20, y: 30 },
  { x: 20, y: 70 },
  { x: 50, y: 20 },
  { x: 50, y: 50 },
  { x: 50, y: 80 },
  { x: 80, y: 35 },
  { x: 80, y: 65 },
]

const LINKS = [
  [0, 3],
  [1, 3],
  [2, 5],
  [3, 5],
  [3, 6],
  [4, 6],
]

export default function BrandPanel({ title, description }) {
  const [activeLink, setActiveLink] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveLink((i) => (i + 1) % LINKS.length)
    }, 1400)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="hidden flex-col justify-center bg-surface px-12 lg:flex lg:w-1/2">
      <svg viewBox="0 0 100 100" className="mb-8 h-40 w-40">
        {LINKS.map(([a, b], i) => (
          <line
            key={i}
            x1={NODES[a].x}
            y1={NODES[a].y}
            x2={NODES[b].x}
            y2={NODES[b].y}
            stroke={i === activeLink ? "#60a0f8" : "#3a4453"}
            strokeWidth={i === activeLink ? 1.5 : 1}
            className="transition-all duration-700"
          />
        ))}
        {NODES.map((node, i) => {
          const isActive = LINKS[activeLink].includes(i)
          return (
            <circle
              key={i}
              cx={node.x}
              cy={node.y}
              r={isActive ? 3.5 : 2.5}
              fill={isActive ? "#60a0f8" : "#5c6360"}
              className="transition-all duration-700"
            />
          )
        })}
      </svg>

      <p className="text-sm font-semibold text-blue-400">Matchire</p>
      <h1 className="mt-3 max-w-sm text-4xl font-extrabold leading-tight text-ink">
        {title}
      </h1>
      <p className="mt-4 max-w-xs text-ink-soft">{description}</p>
    </div>
  )
}