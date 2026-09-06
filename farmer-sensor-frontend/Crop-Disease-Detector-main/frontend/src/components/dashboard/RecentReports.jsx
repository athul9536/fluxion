import { ArrowRight, FileText } from 'lucide-react'
import { Link } from 'react-router-dom'
import { formatDate, percent } from '../../utils/format'
import EmptyState from '../ui/EmptyState'
import LoadingState from '../ui/LoadingState'

export default function RecentReports({ reports, loading }) {
  const recent = (reports || []).slice(0, 3)

  return (
    <section className="card">
      <div className="flex items-center justify-between border-b border-leaf-100 px-5 py-4">
        <h2 className="text-lg font-bold text-leaf-900">Recent Detections</h2>
        <Link
          to="/reports"
          className="flex items-center gap-1 text-sm font-semibold text-leaf-700 hover:text-leaf-900"
        >
          View all
          <ArrowRight className="h-4 w-4" aria-hidden="true" />
        </Link>
      </div>

      {loading && recent.length === 0 ? (
        <div className="px-5 py-6">
          <LoadingState label="Loading your reports..." />
        </div>
      ) : recent.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No detections yet"
          description="Scan your first crop photo and your results will appear here."
          action={
            <Link to="/detect" className="btn-primary mt-2">
              Upload Crop Photo
            </Link>
          }
        />
      ) : (
        <ul className="divide-y divide-leaf-100">
          {recent.map((report) => (
            <li key={report.id}>
              <Link
                to={`/reports?report=${report.id}`}
                className="flex items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-leaf-50"
              >
                <div className="min-w-0">
                  <p className="truncate font-semibold text-leaf-900">{report.disease}</p>
                  <p className="mt-0.5 text-xs text-leaf-600">
                    {report.crop} &middot; {formatDate(report.created_at)}
                  </p>
                </div>
                <span className="shrink-0 text-sm font-bold tabular-nums text-leaf-700">
                  {percent(report.confidence)}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
