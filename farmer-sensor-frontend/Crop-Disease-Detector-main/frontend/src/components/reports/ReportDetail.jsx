import { ArrowLeft, MapPin, MessageSquareText, Stethoscope } from 'lucide-react'
import ConfidenceBar from '../detection/ConfidenceBar'
import { formatDate, percent, severityStyle } from '../../utils/format'
import { mediaUrl } from '../../services/api'

function ReportList({ title, items, icon: Icon }) {
  if (!items?.length) return null
  return (
    <div className="mt-5 rounded-xl border border-leaf-100 p-4">
      <p className="label flex items-center gap-1.5">
        {Icon && <Icon className="h-3.5 w-3.5" aria-hidden="true" />}
        {title}
      </p>
      <ul className="mt-2 space-y-1.5">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2 text-sm leading-relaxed text-leaf-800">
            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-leaf-400" aria-hidden="true" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function ReportDetail({ report, onBack, onAskVani }) {
  return (
    <div className="space-y-5">
      <button type="button" onClick={onBack} className="btn-ghost -ml-2 py-2">
        <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        Back to reports
      </button>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card p-5 sm:p-6">
          <p className="label">{formatDate(report.created_at)}</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-leaf-900">{report.disease}</h1>
          <p className="mt-1 text-sm font-medium text-leaf-600">
            {report.crop} &middot; {percent(report.confidence)} confidence
          </p>

          <div className="mt-5">
            <ConfidenceBar confidence={report.confidence} />
          </div>

          <dl className="mt-6 grid grid-cols-2 gap-4">
            <div className={`rounded-xl border p-4 ${severityStyle(report.severity)}`}>
              <dt className="label text-current opacity-80">Severity</dt>
              <dd className="mt-1.5 text-base font-bold">{report.severity}</dd>
            </div>
            <div className="rounded-xl border border-leaf-100 bg-leaf-50/60 p-4">
              <dt className="label">Status</dt>
              <dd className="mt-1.5 text-base font-bold text-leaf-900">{report.status}</dd>
            </div>
          </dl>

          {report.explanation && (
            <div className="mt-5 rounded-xl border border-sky-100 bg-sky-50/70 p-4">
              <p className="label text-sky-800">What Vani Saw</p>
              <p className="mt-2 text-sm leading-relaxed text-leaf-800">{report.explanation}</p>
            </div>
          )}

          <ReportList title="Visible Symptoms" items={report.symptoms} />
          <ReportList title="What You Can Do" items={report.treatment} icon={Stethoscope} />
          <ReportList title="Prevention" items={report.prevention} />

          {report.location_name && (
            <p className="mt-4 flex flex-wrap items-center gap-1.5 text-xs text-leaf-600">
              <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
              {report.location_name}
              {report.pincode && <span className="tabular-nums">&middot; {report.pincode}</span>}
              {report.latitude != null && (
                <span className="text-leaf-500">
                  ({report.latitude.toFixed(2)}, {report.longitude?.toFixed(2)})
                </span>
              )}
            </p>
          )}

          <button type="button" onClick={() => onAskVani(report)} className="btn-primary mt-6 w-full sm:w-auto">
            <MessageSquareText className="h-4 w-4" aria-hidden="true" />
            Ask Vani about this result
          </button>
        </div>

        {report.image_url && (
          <div className="card overflow-hidden">
            <div className="border-b border-leaf-100 px-5 py-3">
              <p className="label">Analyzed Photo</p>
            </div>
            <img
              src={mediaUrl(report.image_url)}
              alt={`Crop photo analyzed on ${formatDate(report.created_at)}`}
              className="max-h-96 w-full object-contain"
            />
          </div>
        )}
      </div>
    </div>
  )
}
