import { useCallback, useEffect, useState } from 'react'

const STORAGE_KEY = 'vani.farmLocation'
const EMPTY = { address: '', pincode: '' }

/**
 * Farmer-entered address and pincode, persisted in localStorage.
 *
 * Only the pincode reaches the backend, and only for diseased scans. The
 * address is kept purely on the device for the farmer's own reference.
 */
export function useFarmLocation() {
  const [location, setLocation] = useState(EMPTY)

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY)
      if (raw) setLocation({ ...EMPTY, ...JSON.parse(raw) })
    } catch {
      // Corrupt or unavailable storage is not worth surfacing to the farmer.
    }
  }, [])

  const save = useCallback((next) => {
    const value = {
      address: (next.address || '').trim(),
      pincode: (next.pincode || '').replace(/\D/g, '').slice(0, 6),
    }
    setLocation(value)
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
    } catch {
      // Ignore quota or private-mode failures; state still updates.
    }
    return value
  }, [])

  const clear = useCallback(() => {
    setLocation(EMPTY)
    try {
      window.localStorage.removeItem(STORAGE_KEY)
    } catch {
      // Nothing useful to do here.
    }
  }, [])

  return { location, save, clear }
}
