import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { useFarmLocation } from '../hooks/useFarmLocation'
import { useGeolocation } from '../hooks/useGeolocation'
import { useReports } from '../hooks/useReports'
import { useWeather } from '../hooks/useWeather'

const DashboardContext = createContext(null)

const GREETING_MESSAGE = {
  id: 'welcome',
  role: 'assistant',
  text:
    "Hello! I'm Vani, your farming companion. Ask me anything about plants — crops, " +
    'vegetables, fruit trees, spices, or even the pots on your terrace. Diseases, ' +
    'fertilizer, watering, soil, pests, pruning, monsoon planning: it all counts.\n\n' +
    'One thing to know: this chat is text only. If you want a photo checked, open ' +
    'Disease Detection from the menu and upload it there, then tap "Ask Vani About ' +
    'This" to come back and talk it through with me.\n\n' +
    'So, what are you growing at the moment?',
  at: new Date().toISOString(),
}

export function DashboardProvider({ children }) {
  const { location } = useGeolocation()
  const weather = useWeather(location)
  const reports = useReports()
  const farmLocation = useFarmLocation()

  // Chat lives here so the detection page can hand context to the assistant.
  const [messages, setMessages] = useState([GREETING_MESSAGE])
  const [detectionContext, setDetectionContext] = useState(null)
  const [pendingQuestion, setPendingQuestion] = useState(null)
  const [lastDetection, setLastDetection] = useState(null)

  const resetChat = useCallback(() => {
    setMessages([GREETING_MESSAGE])
    setDetectionContext(null)
  }, [])

  const value = useMemo(
    () => ({
      location,
      weather,
      reports,
      farmLocation,
      messages,
      setMessages,
      detectionContext,
      setDetectionContext,
      pendingQuestion,
      setPendingQuestion,
      lastDetection,
      setLastDetection,
      resetChat,
    }),
    [
      location,
      weather,
      reports,
      farmLocation,
      messages,
      detectionContext,
      pendingQuestion,
      lastDetection,
      resetChat,
    ],
  )

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>
}

export function useDashboard() {
  const ctx = useContext(DashboardContext)
  if (!ctx) throw new Error('useDashboard must be used inside DashboardProvider')
  return ctx
}
