import { Leaf } from 'lucide-react'

export default function TypingIndicator() {
  return (
    <div className="flex animate-fade-up gap-3" role="status" aria-live="polite">
      <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-leaf-600 text-white">
        <Leaf className="h-4 w-4" aria-hidden="true" />
      </span>
      <div className="flex items-center gap-2 rounded-2xl rounded-tl-sm border border-leaf-100 bg-white px-4 py-3 shadow-card">
        <span className="flex gap-1" aria-hidden="true">
          {[0, 150, 300].map((delay) => (
            <span
              key={delay}
              className="h-2 w-2 animate-bounce rounded-full bg-leaf-400"
              style={{ animationDelay: `${delay}ms` }}
            />
          ))}
        </span>
        <span className="text-sm font-medium text-leaf-700">Vani is thinking...</span>
      </div>
    </div>
  )
}
