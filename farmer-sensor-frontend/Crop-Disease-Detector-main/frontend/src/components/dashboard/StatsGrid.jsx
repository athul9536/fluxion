import { Bug, MessageSquareText, ScanLine, Sprout } from 'lucide-react'

const CARDS = [
  { key: 'crops_scanned', label: 'Crops Scanned', icon: ScanLine, tone: 'text-leaf-600 bg-leaf-100' },
  { key: 'diseases_detected', label: 'Diseases Detected', icon: Bug, tone: 'text-amber-700 bg-amber-100' },
  { key: 'healthy_plants', label: 'Healthy Plants', icon: Sprout, tone: 'text-leaf-700 bg-leaf-100' },
  { key: 'questions_asked', label: 'Questions Asked', icon: MessageSquareText, tone: 'text-sky-700 bg-sky-100' },
]

export default function StatsGrid({ stats, loading }) {
  return (
    <section aria-label="Farm activity summary" className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {CARDS.map(({ key, label, icon: Icon, tone }) => (
        <article key={key} className="card p-5">
          <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${tone}`}>
            <Icon className="h-5 w-5" aria-hidden="true" />
          </span>
          <p className="mt-4 text-3xl font-bold tabular-nums text-leaf-900">
            {loading && !stats ? (
              <span className="inline-block h-8 w-10 animate-pulse rounded bg-leaf-100" />
            ) : (
              (stats?.[key] ?? 0)
            )}
          </p>
          <p className="mt-1 text-sm font-medium text-leaf-700">{label}</p>
        </article>
      ))}
    </section>
  )
}
