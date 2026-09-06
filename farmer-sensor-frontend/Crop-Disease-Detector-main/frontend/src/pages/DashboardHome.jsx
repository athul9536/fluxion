import { MessageSquareText, ScanLine } from 'lucide-react'
import ActionCard from '../components/dashboard/ActionCard'
import StatsGrid from '../components/dashboard/StatsGrid'
import WeatherCard from '../components/dashboard/WeatherCard'
import RecentReports from '../components/dashboard/RecentReports'
import { useDashboard } from '../context/DashboardContext'
import { greeting } from '../utils/format'

export default function DashboardHome() {
  const { weather, reports } = useDashboard()

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold tracking-tight text-leaf-900 sm:text-4xl">
          {greeting()}, Farmer
        </h1>
        <p className="mt-2 max-w-xl text-base text-leaf-700">
          Monitor your crops and get AI-powered agricultural advice.
        </p>
      </header>

      <WeatherCard
        weather={weather.weather}
        loading={weather.loading}
        error={weather.error}
        onReload={weather.reload}
      />

      <StatsGrid stats={reports.stats} loading={reports.loading} />

      <section className="grid gap-5 lg:grid-cols-2">
        <ActionCard
          icon={ScanLine}
          title="Scan Your Crop"
          description="Upload a photo of your crop to detect possible diseases using AI."
          cta="Upload Crop Photo"
          to="/detect"
        />
        <ActionCard
          icon={MessageSquareText}
          title="Ask Vani AI"
          description="Have a question about your crops? Ask our agricultural assistant."
          cta="Ask a Question"
          to="/assistant"
          accent="sky"
        />
      </section>

      <RecentReports reports={reports.reports} loading={reports.loading} />
    </div>
  )
}
