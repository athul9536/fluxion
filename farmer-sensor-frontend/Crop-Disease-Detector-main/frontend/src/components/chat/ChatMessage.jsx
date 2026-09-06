import { Leaf, User } from 'lucide-react'
import { formatTime } from '../../utils/format'

export default function ChatMessage({ message }) {
  const isFarmer = message.role === 'farmer'

  return (
    <div className={`flex animate-fade-up gap-3 ${isFarmer ? 'flex-row-reverse' : ''}`}>
      <span
        className={[
          'mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl',
          isFarmer ? 'bg-soil-100 text-soil-700' : 'bg-leaf-600 text-white',
        ].join(' ')}
        aria-hidden="true"
      >
        {isFarmer ? <User className="h-4 w-4" /> : <Leaf className="h-4 w-4" />}
      </span>

      <div className={`max-w-[85%] sm:max-w-[75%] ${isFarmer ? 'items-end text-right' : ''}`}>
        <div
          className={[
            'rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-card',
            isFarmer
              ? 'rounded-tr-sm bg-leaf-600 text-left text-white'
              : 'rounded-tl-sm border border-leaf-100 bg-white text-leaf-900',
          ].join(' ')}
        >
          <p className="whitespace-pre-wrap">{message.text}</p>
        </div>

        <div
          className={`mt-1.5 flex flex-wrap items-center gap-2 px-1 text-[11px] text-leaf-600 ${
            isFarmer ? 'justify-end' : ''
          }`}
        >
          <span>
            {isFarmer ? 'You' : 'Vani AI'} &middot; {formatTime(message.at)}
          </span>
          {message.contextNote && (
            <span className="rounded-full border border-leaf-200 bg-leaf-50 px-2 py-0.5 font-semibold text-leaf-700">
              {message.contextNote}
            </span>
          )}
          {message.sources?.length > 0 && (
            <span className="rounded-full border border-leaf-100 bg-leaf-50 px-2 py-0.5">
              Source: {message.sources[0]}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
