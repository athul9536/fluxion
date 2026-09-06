import { useCallback, useEffect, useState } from 'react'
import { getReportStats, getReports } from '../services/api'

export function useReports() {
  const [reports, setReports] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [list, summary] = await Promise.all([getReports(), getReportStats()])
      setReports(list || [])
      setStats(summary)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return { reports, stats, loading, error, reload: load }
}
