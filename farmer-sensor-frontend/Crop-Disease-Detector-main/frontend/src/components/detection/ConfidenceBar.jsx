import { confidenceTone, percent } from '../../utils/format'

export default function ConfidenceBar({ confidence = 0, label = 'Confidence' }) {
  const value = Math.round((confidence ?? 0) * 100)
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <span className="label">{label}</span>
        <span className="text-sm font-bold tabular-nums text-leaf-900">{percent(confidence)}</span>
      </div>
      <div
        className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-leaf-100"
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${label} ${value} percent`}
      >
        <div
          className={`h-full rounded-full transition-all duration-700 ${confidenceTone(confidence)}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  )
}
