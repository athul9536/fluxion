import { Brain, MapPin, ScanLine, ShieldCheck, User } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useDashboard } from '../context/DashboardContext'
import { getHealth } from '../services/api'

const ASSISTANT_LABELS = {
  'azure-openai': 'Azure OpenAI',
  claude: 'Claude',
  'local-context': 'Local context',
}

function Row({ icon: Icon, label, value, hint }) {
  return (
    <div className="flex items-start gap-4 px-5 py-4">
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-leaf-100 text-leaf-700">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold text-leaf-900">{label}</p>
        {hint && <p className="mt-0.5 text-xs text-leaf-600">{hint}</p>}
      </div>
      <p className="shrink-0 text-sm font-medium text-leaf-700">{value}</p>
    </div>
  )
}

export default function Settings() {
  const { location, weather } = useDashboard()
  const [health, setHealth] = useState(null)

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth(null))
  }, [])

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold tracking-tight text-leaf-900 sm:text-4xl">Settings</h1>
        <p className="mt-2 text-base text-leaf-700">
          Your account and the services powering this dashboard.
        </p>
      </header>

      <section className="card divide-y divide-leaf-100">
        <div className="px-5 py-4">
          <h2 className="text-lg font-bold text-leaf-900">Account</h2>
        </div>
        <Row icon={User} label="Plan" value="Premium Farmer" hint="Full dashboard access" />
        <Row
          icon={MapPin}
          label="Field location"
          value={weather.weather?.location || 'Default location'}
          hint={
            location
              ? `From your browser (${location.latitude.toFixed(2)}, ${location.longitude.toFixed(2)})`
              : 'Using the default location configured on the backend'
          }
        />
      </section>

      <section className="card divide-y divide-leaf-100">
        <div className="px-5 py-4">
          <h2 className="text-lg font-bold text-leaf-900">Services</h2>
        </div>
        <Row
          icon={ScanLine}
          label="Disease analysis"
          value={health?.detector === 'claude-vision' ? 'Claude Vision' : 'Not configured'}
          hint={
            health?.vision_model
              ? `Model: ${health.vision_model}`
              : 'Set ANTHROPIC_API_KEY on the backend to enable image analysis'
          }
        />
        <Row
          icon={Brain}
          label="AI assistant"
          value={ASSISTANT_LABELS[health?.assistant] || 'Local context'}
          hint={
            health?.assistant_model
              ? `Model: ${health.assistant_model} (text only)`
              : 'Set ASSISTANT_API_KEY on the backend for full AI answers'
          }
        />
        <Row
          icon={ShieldCheck}
          label="Weather source"
          value={weather.weather?.source === 'openweathermap' ? 'OpenWeatherMap' : 'Demo data'}
          hint="Set OPENWEATHER_API_KEY on the backend for live weather"
        />
      </section>
    </div>
  )
}
