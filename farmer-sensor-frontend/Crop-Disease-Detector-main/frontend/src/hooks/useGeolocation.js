import { useEffect, useState } from 'react'

/**
 * Best-effort browser geolocation. The backend applies the configured default
 * location whenever coordinates are unavailable, so failure is never blocking.
 */
export function useGeolocation() {
  const [location, setLocation] = useState(null)
  const [resolved, setResolved] = useState(false)

  useEffect(() => {
    if (!navigator.geolocation) {
      setResolved(true)
      return
    }
    let active = true
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        if (!active) return
        setLocation({ latitude: coords.latitude, longitude: coords.longitude })
        setResolved(true)
      },
      () => active && setResolved(true),
      { timeout: 8000, maximumAge: 600000 },
    )
    return () => {
      active = false
    }
  }, [])

  return { location, resolved }
}
