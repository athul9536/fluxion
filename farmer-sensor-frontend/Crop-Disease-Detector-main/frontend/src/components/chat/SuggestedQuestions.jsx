import { Sparkles } from 'lucide-react'

export const SUGGESTIONS = [
  'Why are my leaves turning yellow?',
  'When should I fertilize my coconut?',
  'How often should I irrigate rice?',
  'What diseases are common during monsoon?',
  'How do I start a compost pit?',
  'Which vegetables grow well on a terrace?',
  'How do I keep pests off my chilli plants?',
]

export default function SuggestedQuestions({ onPick, disabled }) {
  return (
    <div>
      <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-leaf-600">
        <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
        Suggested questions
      </p>
      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((question) => (
          <button
            key={question}
            type="button"
            disabled={disabled}
            onClick={() => onPick(question)}
            className="rounded-full border border-leaf-200 bg-white px-3.5 py-2 text-xs font-medium text-leaf-700 transition-colors hover:border-leaf-400 hover:bg-leaf-50 disabled:opacity-50"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  )
}
