import { useCallback, useEffect, useState } from 'react'
import { getWeather } from '../services/api'

export function useWeather(location) {
  const [weather, setWeather] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setWeather(await getWeather(location || {}))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [location?.latitude, location?.longitude])

  useEffect(() => {
    load()
  }, [load])

  return { weather, loading, error, reload: load }
}
