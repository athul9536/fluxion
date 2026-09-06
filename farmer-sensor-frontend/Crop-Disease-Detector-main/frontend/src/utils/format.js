export const percent = (value) => `${Math.round((value ?? 0) * 100)}%`

export function formatDate(value) {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '--'
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export function formatTime(value) {
  const date = value ? new Date(value) : new Date()
  return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
}

export function greeting(date = new Date()) {
  const hour = date.getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

export const SEVERITY_STYLES = {
  Severe: 'bg-red-50 text-red-700 border-red-200',
  Moderate: 'bg-amber-50 text-amber-800 border-amber-200',
  Mild: 'bg-sky-50 text-sky-800 border-sky-200',
  Healthy: 'bg-leaf-100 text-leaf-800 border-leaf-200',
  Unknown: 'bg-leaf-50 text-leaf-700 border-leaf-200',
  None: 'bg-leaf-100 text-leaf-800 border-leaf-200',
}

export const severityStyle = (severity) =>
  SEVERITY_STYLES[severity] || SEVERITY_STYLES.Unknown

export const confidenceTone = (confidence) => {
  if (confidence >= 0.75) return 'bg-leaf-600'
  if (confidence >= 0.4) return 'bg-amber-500'
  return 'bg-leaf-300'
}
