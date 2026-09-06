/**
 * Single place where the dashboard talks to FastAPI.
 * Every failure is converted into a short, farmer-friendly message.
 */
const BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
const TIMEOUT_MS = 45000

const FALLBACK = {
  offline: "We can't reach the Vani service right now. Please check your connection and try again.",
  timeout: 'That took longer than expected. Please try again in a moment.',
  generic: 'Something went wrong. Please try again.',
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request(path, { method = 'GET', body, headers, timeout = TIMEOUT_MS } = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)

  let response
  try {
    response = await fetch(`${BASE}${path}`, {
      method,
      body,
      headers,
      signal: controller.signal,
    })
  } catch (error) {
    clearTimeout(timer)
    throw new ApiError(error.name === 'AbortError' ? FALLBACK.timeout : FALLBACK.offline, 0)
  }
  clearTimeout(timer)

  let payload = null
  try {
    payload = await response.json()
  } catch {
    payload = null
  }

  if (!response.ok) {
    const detail = typeof payload?.detail === 'string' ? payload.detail : FALLBACK.generic
    throw new ApiError(detail, response.status)
  }
  return payload
}

export const getWeather = ({ latitude, longitude } = {}) => {
  const query =
    latitude != null && longitude != null ? `?lat=${latitude}&lon=${longitude}` : ''
  return request(`/api/weather${query}`, { timeout: 12000 })
}

export const getReports = () => request('/api/reports', { timeout: 15000 })

export const getReportStats = () => request('/api/reports/stats', { timeout: 15000 })

export function detectDisease({ file, location, pincode }) {
  const form = new FormData()
  form.append('image', file)
  if (location?.latitude != null) form.append('latitude', location.latitude)
  if (location?.longitude != null) form.append('longitude', location.longitude)
  if (location?.name) form.append('location_name', location.name)
  // The backend stores this only when a disease is detected.
  if (pincode) form.append('pincode', pincode)
  return request('/api/detect', { method: 'POST', body: form })
}

export const askVani = ({ message, context, image, detectionContext, history }) =>
  request('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      context,
      image: image || null,
      detection_context: detectionContext || null,
      history: history || [],
    }),
  })

export const getHealth = () => request('/api/health', { timeout: 8000 })

export const mediaUrl = (path) => (path ? `${BASE}${path}` : null)
