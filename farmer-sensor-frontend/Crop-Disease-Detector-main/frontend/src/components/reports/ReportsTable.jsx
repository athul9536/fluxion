import { ChevronRight } from 'lucide-react'
import { formatDate, percent, severityStyle } from '../../utils/format'

const StatusPill = ({ report }) => (
  <span
    className={`inline-block rounded-full border px-2.5 py-1 text-xs font-semibold ${severityStyle(
      report.severity,
    )}`}
  >
    {report.status}
  </span>
)

export default function ReportsTable({ reports, onSelect }) {
  return (
    <>
      {/* Desktop table */}
      <div className="hidden overflow-x-auto md:block">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-leaf-100 bg-leaf-50/60">
            <tr className="text-xs uppercase tracking-wider text-leaf-600">
              <th scope="col" className="px-5 py-3 font-semibold">Date</th>
              <th scope="col" className="px-5 py-3 font-semibold">Crop</th>
              <th scope="col" className="px-5 py-3 font-semibold">Disease</th>
              <th scope="col" className="px-5 py-3 font-semibold">Confidence</th>
              <th scope="col" className="px-5 py-3 font-semibold">Location</th>
              <th scope="col" className="px-5 py-3 font-semibold">Status</th>
              <th scope="col" className="px-5 py-3">
                <span className="sr-only">Open</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-leaf-100">
            {reports.map((report) => (
              <tr
                key={report.id}
                onClick={() => onSelect(report)}
                className="cursor-pointer transition-colors hover:bg-leaf-50"
              >
                <td className="px-5 py-4 text-leaf-700">{formatDate(report.created_at)}</td>
                <td className="px-5 py-4 font-medium text-leaf-900">{report.crop}</td>
                <td className="px-5 py-4 font-semibold text-leaf-900">{report.disease}</td>
                <td className="px-5 py-4 font-bold tabular-nums text-leaf-700">
                  {percent(report.confidence)}
                </td>
                <td className="px-5 py-4 text-leaf-700">
                  {report.location_name || '--'}
                  {report.pincode && (
                    <span className="block text-xs tabular-nums text-leaf-500">
                      {report.pincode}
                    </span>
                  )}
                </td>
                <td className="px-5 py-4">
                  <StatusPill report={report} />
                </td>
                <td className="px-5 py-4 text-right">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation()
                      onSelect(report)
                    }}
                    className="text-leaf-600 hover:text-leaf-900"
                    aria-label={`Open ${report.disease} report from ${formatDate(report.created_at)}`}
                  >
                    <ChevronRight className="h-4 w-4" aria-hidden="true" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <ul className="divide-y divide-leaf-100 md:hidden">
        {reports.map((report) => (
          <li key={report.id}>
            <button
              type="button"
              onClick={() => onSelect(report)}
              className="flex w-full items-center justify-between gap-3 px-4 py-4 text-left transition-colors hover:bg-leaf-50"
            >
              <div className="min-w-0">
                <p className="truncate font-semibold text-leaf-900">{report.disease}</p>
                <p className="mt-0.5 text-xs text-leaf-600">
                  {report.crop} &middot; {formatDate(report.created_at)}
                </p>
                <p className="mt-1.5 truncate text-xs text-leaf-600">
                  {report.location_name || '--'}
                  {report.pincode && <span className="tabular-nums"> &middot; {report.pincode}</span>}
                </p>
                <span className="mt-2 inline-block">
                  <StatusPill report={report} />
                </span>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <span className="text-base font-bold tabular-nums text-leaf-700">
                  {percent(report.confidence)}
                </span>
                <ChevronRight className="h-4 w-4 text-leaf-400" aria-hidden="true" />
              </div>
            </button>
          </li>
        ))}
      </ul>
    </>
  )
}
