import { FileText, RefreshCw } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import ReportDetail from '../components/reports/ReportDetail'
import ReportsTable from '../components/reports/ReportsTable'
import EmptyState from '../components/ui/EmptyState'
import ErrorMessage from '../components/ui/ErrorMessage'
import LoadingState from '../components/ui/LoadingState'
import { useDashboard } from '../context/DashboardContext'

export default function MyReports() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()
  const { reports, setDetectionContext, setPendingQuestion } = useDashboard()
  const [selected, setSelected] = useState(null)

  // Deep link support: /reports?report=12
  useEffect(() => {
    const id = params.get('report')
    if (!id) {
      setSelected(null)
      return
    }
    const match = reports.reports.find((r) => String(r.id) === id)
    if (match) setSelected(match)
  }, [params, reports.reports])

  const open = (report) => {
    setSelected(report)
    setParams({ report: String(report.id) })
  }

  const back = () => {
    setSelected(null)
    setParams({})
  }

  const askVani = (report) => {
    setDetectionContext({
      crop: report.crop,
      disease: report.disease,
      confidence: report.confidence,
      severity: report.severity,
      symptoms: report.symptoms || [],
      treatment: report.treatment || [],
      explanation: report.explanation || null,
      image_url: report.image_url || null,
    })
    setPendingQuestion('Tell me more about this result.')
    navigate('/assistant')
  }

  if (selected) {
    return <ReportDetail report={selected} onBack={back} onAskVani={askVani} />
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-leaf-900 sm:text-4xl">My Reports</h1>
          <p className="mt-2 text-base text-leaf-700">
            Every crop scan you have run, with the diagnosis and advice saved.
          </p>
        </div>
        <button type="button" onClick={reports.reload} className="btn-secondary py-2.5">
          <RefreshCw className={`h-4 w-4 ${reports.loading ? 'animate-spin' : ''}`} aria-hidden="true" />
          Refresh
        </button>
      </header>

      <ErrorMessage message={reports.error} onRetry={reports.reload} />

      <section className="card overflow-hidden">
        {reports.loading && reports.reports.length === 0 ? (
          <div className="px-5 py-8">
            <LoadingState label="Loading your reports..." />
          </div>
        ) : reports.reports.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No reports yet"
            description="Once you analyze a crop photo, the diagnosis and treatment advice are saved here."
            action={
              <Link to="/detect" className="btn-primary mt-2">
                Scan Your Crop
              </Link>
            }
          />
        ) : (
          <ReportsTable reports={reports.reports} onSelect={open} />
        )}
      </section>
    </div>
  )
}
