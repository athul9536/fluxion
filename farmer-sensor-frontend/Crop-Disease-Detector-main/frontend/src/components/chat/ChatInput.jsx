import { Send } from 'lucide-react'
import { useEffect, useRef } from 'react'
import Spinner from '../ui/Spinner'

export default function ChatInput({ value, onChange, onSend, sending }) {
  const ref = useRef(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`
  }, [value])

  const submit = (e) => {
    e.preventDefault()
    if (!value.trim() || sending) return
    onSend(value)
  }

  return (
    <form onSubmit={submit} className="flex items-end gap-2">
      <label htmlFor="chat-input" className="sr-only">
        Ask Vani about your crops
      </label>
      <textarea
        id="chat-input"
        ref={ref}
        rows={1}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) submit(e)
        }}
        placeholder="Ask Vani about your crops..."
        className="max-h-36 min-h-[52px] flex-1 resize-none rounded-xl border border-leaf-200 bg-white px-4 py-3.5 text-sm text-leaf-900 placeholder:text-leaf-400 focus:border-leaf-500"
      />
      <button
        type="submit"
        disabled={sending || !value.trim()}
        className="btn-primary h-[52px] w-[52px] shrink-0 !px-0"
        aria-label="Send question"
      >
        {sending ? <Spinner /> : <Send className="h-5 w-5" aria-hidden="true" />}
      </button>
    </form>
  )
}
