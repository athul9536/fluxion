import Spinner from './Spinner'

export default function LoadingState({ label, className = '' }) {
  return (
    <div
      className={`flex items-center gap-3 text-sm font-medium text-leaf-700 ${className}`}
      role="status"
      aria-live="polite"
    >
      <Spinner className="h-4 w-4 text-leaf-600" />
      <span>{label}</span>
    </div>
  )
}
