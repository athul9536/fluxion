import { Loader2, MapPin, ScanLine } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import DetectionResult from '../components/detection/DetectionResult'
import ImageUploader from '../components/detection/ImageUploader'
import ErrorMessage from '../components/ui/ErrorMessage'
import { useDashboard } from '../context/DashboardContext'
import { detectDisease, mediaUrl } from '../services/api'

export default function DiseaseDetection() {
  const navigate = useNavigate()
  const {
    location,
    reports,
    farmLocation,
    setDetectionContext,
    setPendingQuestion,
    lastDetection,
    setLastDetection,
  } = useDashboard()

  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(lastDetection?.result ?? null)
  const [resultImage, setResultImage] = useState(lastDetection?.image ?? null)

  useEffect(() => {
    if (!file) return
    const url = URL.createObjectURL(file)
    setPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  const clear = () => {
    setFile(null)
    setPreview(null)
    setError(null)
  }

  const analyze = async () => {
    if (!file) return
    setAnalyzing(true)
    setError(null)
    // Clear any previous result so a failed analysis can never sit next to a
    // stale diagnosis from an earlier photo.
    setResult(null)
    setResultImage(null)
    setLastDetection(null)
    try {
      const data = await detectDisease({
        file,
        location,
        pincode: farmLocation.location.pincode,
      })
      setResult(data)
      const image = preview
      setResultImage(image)
      setLastDetection({ result: data, image })
      reports.reload()
    } catch (err) {
      setError(err.message)
    } finally {
      setAnalyzing(false)
    }
  }

  const askVani = () => {
    if (!result) return
    setDetectionContext({
      crop: result.crop,
      disease: result.disease,
      confidence: result.confidence,
      severity: result.severity,
      symptoms: result.symptoms || [],
      treatment: result.treatment || [],
      explanation: result.explanation || null,
      image_url: result.image_url || null,
    })
    setPendingQuestion('Tell me more about this result.')
    navigate('/assistant')
  }

  return (
    <div className="space-y-6">
      <header>
        <p className="flex items-center gap-2 text-sm font-semibold text-leaf-600">
          <ScanLine className="h-4 w-4" aria-hidden="true" />
          AI Crop Diagnosis
        </p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-leaf-900 sm:text-4xl">
          Disease Detection
        </h1>
        <p className="mt-2 max-w-xl text-base text-leaf-700">
          Take a clear photo of the affected leaf in daylight for the most reliable result.
        </p>
      </header>

      <ErrorMessage message={error} onRetry={file ? analyze : undefined} retryLabel="Analyze again" />

      {!farmLocation.location.pincode && (
        <p className="flex flex-wrap items-center gap-1 rounded-xl border border-leaf-100 bg-leaf-50 px-4 py-3 text-xs text-leaf-700">
          <MapPin className="h-3.5 w-3.5 shrink-0 text-leaf-600" aria-hidden="true" />
          Add your pincode in
          <Link
            to="/location"
            className="font-semibold text-leaf-800 underline decoration-leaf-300 hover:text-leaf-900"
          >
            Location
          </Link>
          so disease reports can be tracked by area.
        </p>
      )}

      <ImageUploader
        file={file}
        preview={preview}
        analyzing={analyzing}
        onSelect={(picked) => {
          setFile(picked)
          setError(null)
          // A new photo invalidates the previous diagnosis.
          setResult(null)
          setResultImage(null)
        }}
        onClear={clear}
        onAnalyze={analyze}
        onValidationError={setError}
      />

      {analyzing && (
        <section className="card flex flex-col items-center gap-3 px-6 py-10 text-center" aria-live="polite">
          <Loader2 className="h-8 w-8 animate-spin text-leaf-600" aria-hidden="true" />
          <p className="text-base font-semibold text-leaf-900">Analyzing your crop...</p>
          <p className="text-sm text-leaf-600">
            Vani AI is examining your photo for disease signs. This takes a few seconds.
          </p>
        </section>
      )}

      {!analyzing && result && (
        <DetectionResult
          result={result}
          // Prefer the backend-served copy: the local blob URL is revoked as
          // soon as the selected file changes, which left a broken image.
          imageSrc={mediaUrl(result.image_url) || resultImage}
          onAskVani={askVani}
        />
      )}
    </div>
  )
}
