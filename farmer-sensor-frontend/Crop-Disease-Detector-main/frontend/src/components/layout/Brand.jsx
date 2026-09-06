import { Leaf } from 'lucide-react'

export default function Brand({ compact = false }) {
  return (
    <div className="flex items-center gap-3">
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-leaf-600 text-white shadow-card">
        <Leaf className="h-5 w-5" aria-hidden="true" />
      </span>
      <span className="leading-tight">
        <span className="block text-base font-bold tracking-tight text-leaf-900">VANI</span>
        {!compact && (
          <span className="block text-xs font-medium text-leaf-600">Network Intelligence</span>
        )}
      </span>
    </div>
  )
}
