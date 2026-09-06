import { CloudRain, CloudSun, Droplets, MapPin, RefreshCw, Sun, Wind } from 'lucide-react'
import ErrorMessage from '../ui/ErrorMessage'
import LoadingState from '../ui/LoadingState'

const iconFor = (condition = '') => {
  const c = condition.toLowerCase()
  if (c.includes('rain') || c.includes('drizzle') || c.includes('thunder')) return CloudRain
  if (c.includes('cloud')) return CloudSun
  return Sun
}

export default function WeatherCard({ weather, loading, error, onReload }) {
  if (loading && !weather) {
    return (
      <section className="card p-6">
        <LoadingState label="Updating weather..." />
      </section>
    )
  }

  if (error && !weather) {
    return (
      <section className="card p-6">
        <ErrorMessage message={error} onRetry={onReload} />
      </section>
    )
  }

  if (!weather) return null
  const Icon = iconFor(weather.condition)

  return (
    <section className="card overflow-hidden">
      <div className="flex flex-col gap-6 bg-gradient-to-br from-leaf-600 to-leaf-700 p-6 text-white sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-5">
          <span className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-white/15">
            <Icon className="h-9 w-9" aria-hidden="true" />
          </span>
          <div>
            <p className="text-4xl font-bold leading-none sm:text-5xl">
              {Math.round(weather.temperature)}
              <span className="align-top text-2xl">&deg;C</span>
            </p>
            <p className="mt-1.5 text-sm font-medium text-leaf-100">{weather.description}</p>
          </div>
        </div>

        <dl className="grid grid-cols-2 gap-4 sm:text-right">
          <div className="flex items-center gap-2 sm:justify-end">
            <Droplets className="h-4 w-4 text-leaf-200" aria-hidden="true" />
            <div>
              <dt className="text-[11px] uppercase tracking-wide text-leaf-200">Humidity</dt>
              <dd className="text-base font-semibold">{weather.humidity}%</dd>
            </div>
          </div>
          <div className="flex items-center gap-2 sm:justify-end">
            <Wind className="h-4 w-4 text-leaf-200" aria-hidden="true" />
            <div>
              <dt className="text-[11px] uppercase tracking-wide text-leaf-200">Wind</dt>
              <dd className="text-base font-semibold">{weather.wind_speed ?? 0} m/s</dd>
            </div>
          </div>
        </dl>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-4">
        <p className="flex items-center gap-2 text-sm font-medium text-leaf-800">
          <MapPin className="h-4 w-4 text-leaf-600" aria-hidden="true" />
          {weather.location}
        </p>
        <div className="flex items-center gap-3">
          {weather.rain_expected && (
            <span className="rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-800">
              Rain expected
            </span>
          )}
          {weather.source !== 'openweathermap' && (
            <span className="rounded-full border border-soil-200 bg-soil-50 px-3 py-1 text-xs font-semibold text-soil-700">
              Demo weather
            </span>
          )}
          <button
            type="button"
            onClick={onReload}
            className="flex items-center gap-1.5 text-xs font-semibold text-leaf-700 hover:text-leaf-900"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} aria-hidden="true" />
            Refresh
          </button>
        </div>
      </div>
    </section>
  )
}
