import {
  CheckCircle2,
  HelpCircle,
  Info,
  Leaf,
  MapPin,
  MessageSquareText,
  ShieldAlert,
  ShieldCheck,
  Sprout,
  Stethoscope,
} from 'lucide-react'
import { percent, severityStyle } from '../../utils/format'
import ConfidenceBar from './ConfidenceBar'

function BulletList({ icon: Icon, title, items, tone = 'text-leaf-600' }) {
  if (!items?.length) return null
  return (
    <div className="rounded-xl border border-leaf-100 bg-white p-4">
      <p className="label flex items-center gap-1.5">
        <Icon className={`h-3.5 w-3.5 ${tone}`} aria-hidden="true" />
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

export default function DetectionResult({ result, imageSrc, onAskVani }) {
  if (!result) return null

  const healthy = result.severity === 'Healthy'
  const undetermined = (result.disease || '').trim().toLowerCase() === 'unable to determine'

  const badge = undetermined
    ? { text: 'Needs a clearer photo', cls: 'border-sky-200 bg-sky-50 text-sky-800', Icon: HelpCircle }
    : healthy
      ? { text: 'No disease detected', cls: 'border-leaf-200 bg-leaf-100 text-leaf-800', Icon: CheckCircle2 }
      : { text: 'Disease analysis', cls: 'border-amber-200 bg-amber-50 text-amber-800', Icon: ShieldAlert }

  return (
    <section className="grid animate-fade-up gap-5 lg:grid-cols-2">
      {imageSrc && (
        <div className="card overflow-hidden lg:order-2">
          <div className="border-b border-leaf-100 px-5 py-3">
            <p className="label">Analyzed Photo</p>
          </div>
          <img
            src={imageSrc}
            alt="The crop photo that was analyzed"
            className="max-h-96 w-full object-contain"
          />
        </div>
      )}

      <div className="card p-5 sm:p-6 lg:order-1">
        <span
          className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-bold uppercase tracking-wide ${badge.cls}`}
        >
          <badge.Icon className="h-4 w-4" aria-hidden="true" />
          {badge.text}
        </span>

        <p className="label mt-4">Likely Disease</p>
        <h2 className="mt-1 text-3xl font-bold leading-tight text-leaf-900">{result.disease}</h2>

        {!undetermined && (
          <div className="mt-5">
            <ConfidenceBar confidence={result.confidence} label="AI Confidence" />
            <p className="mt-1.5 text-xs text-leaf-600">
              An AI estimate of how well the image matches this condition, not a validated
              probability.
            </p>
          </div>
        )}

        <dl className="mt-6 grid grid-cols-2 gap-4">
          <div className="rounded-xl border border-leaf-100 bg-leaf-50/60 p-4">
            <dt className="label flex items-center gap-1.5">
              <Sprout className="h-3.5 w-3.5" aria-hidden="true" />
              Crop
            </dt>
            <dd className="mt-1.5 text-base font-bold text-leaf-900">{result.crop}</dd>
          </div>
          <div className={`rounded-xl border p-4 ${severityStyle(result.severity)}`}>
            <dt className="label flex items-center gap-1.5 text-current opacity-80">
              <Leaf className="h-3.5 w-3.5" aria-hidden="true" />
              Severity
            </dt>
            <dd className="mt-1.5 text-base font-bold">{result.severity}</dd>
          </div>
        </dl>

        {result.explanation && (
          <div className="mt-5 rounded-xl border border-sky-100 bg-sky-50/70 p-4">
            <p className="label flex items-center gap-1.5 text-sky-800">
              <Info className="h-3.5 w-3.5" aria-hidden="true" />
              What Vani Sees
            </p>
            <p className="mt-2 text-sm leading-relaxed text-leaf-800">{result.explanation}</p>
          </div>
        )}

        <div className="mt-5 space-y-4">
          <BulletList icon={Stethoscope} title="Visible Symptoms" items={result.symptoms} />
          <BulletList icon={Leaf} title="What You Can Do" items={result.treatment} />
          <BulletList icon={ShieldCheck} title="Prevention" items={result.prevention} />
        </div>

        <div className="mt-6 flex flex-col gap-3">
          <button type="button" onClick={onAskVani} className="btn-primary w-full sm:w-auto sm:self-start">
            <MessageSquareText className="h-4 w-4" aria-hidden="true" />
            Ask Vani About This
          </button>

          <p className="rounded-xl border border-soil-200 bg-soil-50 px-4 py-3 text-xs leading-relaxed text-soil-800">
            AI-generated analysis &mdash; confirm serious disease or treatment decisions with a
            qualified agricultural expert.
            {result.needs_expert_confirmation && (
              <span className="mt-1 block font-semibold">
                Vani recommends getting this one checked by an expert.
              </span>
            )}
          </p>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-leaf-600">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-leaf-500" aria-hidden="true" />
              {result.saved ? 'Analysis saved to your reports.' : result.note}
            </span>
            {result.location?.name && (
              <span className="flex items-center gap-1.5">
                <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
                {result.location.name}
                {result.pincode && <span className="tabular-nums">&middot; {result.pincode}</span>}
              </span>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
