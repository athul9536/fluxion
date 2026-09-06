import { ImageOff, Leaf, RotateCcw, X } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import ChatInput from '../components/chat/ChatInput'
import ChatMessage from '../components/chat/ChatMessage'
import SuggestedQuestions from '../components/chat/SuggestedQuestions'
import TypingIndicator from '../components/chat/TypingIndicator'
import ErrorMessage from '../components/ui/ErrorMessage'
import { useDashboard } from '../context/DashboardContext'
import { askVani } from '../services/api'
import { percent } from '../utils/format'

export default function AiAssistant() {
  const {
    messages,
    setMessages,
    detectionContext,
    setDetectionContext,
    pendingQuestion,
    setPendingQuestion,
    location,
    resetChat,
  } = useDashboard()

  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const scrollRef = useRef(null)
  const lastFailed = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, sending])

  const send = useCallback(
    async (text) => {
      const question = text.trim()
      if (!question || sending) return

      const contextNote = detectionContext
        ? `About: ${detectionContext.crop} / ${detectionContext.disease}`
        : null

      setMessages((prev) => [
        ...prev,
        {
          id: `f-${Date.now()}`,
          role: 'farmer',
          text: question,
          at: new Date().toISOString(),
          contextNote,
        },
      ])
      setDraft('')
      setSending(true)
      setError(null)

      try {
        const data = await askVani({
          message: question,
          detectionContext: detectionContext || null,
          // Recent turns keep follow-ups like "and for coconut?" meaningful.
          history: messages
            .filter((m) => m.id !== 'welcome')
            .slice(-8)
            .map((m) => ({
              role: m.role === 'farmer' ? 'user' : 'assistant',
              text: m.text,
            })),
          context: {
            detection: detectionContext || null,
            latitude: location?.latitude ?? null,
            longitude: location?.longitude ?? null,
            include_weather: true,
          },
        })
        setMessages((prev) => [
          ...prev,
          {
            id: `a-${Date.now()}`,
            role: 'assistant',
            text: data.response,
            at: new Date().toISOString(),
            sources: data.sources,
          },
        ])
        lastFailed.current = null
      } catch (err) {
        setError(err.message)
        lastFailed.current = question
      } finally {
        setSending(false)
      }
    },
    [detectionContext, location, sending, setMessages, messages],
  )

  // A detection can hand a question over from the Disease Detection page.
  useEffect(() => {
    if (!pendingQuestion) return
    const question = pendingQuestion
    setPendingQuestion(null)
    send(question)
  }, [pendingQuestion, send, setPendingQuestion])

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <header className="flex items-start justify-between gap-4 pb-4">
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-leaf-600 text-white shadow-card">
            <Leaf className="h-6 w-6" aria-hidden="true" />
          </span>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-leaf-900 sm:text-3xl">Vani AI</h1>
            <p className="text-sm text-leaf-700">Your agricultural assistant</p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => {
            resetChat()
            setError(null)
          }}
          className="btn-ghost py-2 text-xs"
        >
          <RotateCcw className="h-4 w-4" aria-hidden="true" />
          <span className="hidden sm:inline">New chat</span>
        </button>
      </header>

      {detectionContext && (
        <div className="mb-4 flex items-start justify-between gap-3 rounded-xl border border-leaf-200 bg-leaf-50 p-4">
          <div className="min-w-0">
            <p className="label">Detection context attached</p>
            <p className="mt-1 text-sm font-semibold text-leaf-900">
              {detectionContext.crop} &middot; {detectionContext.disease}
              {detectionContext.confidence != null && (
                <span className="font-medium text-leaf-700">
                  {' '}
                  &middot; {percent(detectionContext.confidence)} confidence
                </span>
              )}
            </p>
            <p className="mt-1 text-xs text-leaf-600">
              Vani will use this analysis, its symptoms and treatment steps when answering.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setDetectionContext(null)}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-leaf-700 hover:bg-leaf-100"
            aria-label="Remove detection context"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      )}

      <div className="card flex min-h-0 flex-1 flex-col overflow-hidden">
        <div
          ref={scrollRef}
          className="scrollbar-slim min-h-[280px] flex-1 space-y-5 overflow-y-auto bg-leaf-50/40 p-4 sm:p-5"
        >
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {sending && <TypingIndicator />}
        </div>

        <div className="space-y-3 border-t border-leaf-100 bg-white p-4">
          {error && (
            <ErrorMessage
              message={error}
              onRetry={lastFailed.current ? () => send(lastFailed.current) : undefined}
              retryLabel="Resend"
            />
          )}
          <SuggestedQuestions onPick={send} disabled={sending} />
          <ChatInput value={draft} onChange={setDraft} onSend={send} sending={sending} />
          <p className="flex flex-wrap items-center gap-1 text-[11px] text-leaf-500">
            <ImageOff className="h-3 w-3 shrink-0" aria-hidden="true" />
            Text only &mdash; no photo uploads here. To check a photo, use
            <Link
              to="/detect"
              className="font-semibold text-leaf-700 underline decoration-leaf-300 hover:text-leaf-900"
            >
              Disease Detection
            </Link>
            . Confirm chemical doses with your local Krishi Bhavan.
          </p>
        </div>
      </div>
    </div>
  )
}
