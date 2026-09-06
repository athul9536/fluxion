import { ImagePlus, Trash2, UploadCloud } from 'lucide-react'
import { useRef, useState } from 'react'
import Spinner from '../ui/Spinner'

const MAX_BYTES = 8 * 1024 * 1024
const TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']

export default function ImageUploader({
  file,
  preview,
  analyzing,
  onSelect,
  onClear,
  onAnalyze,
  onValidationError,
}) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  const handleFiles = (files) => {
    const picked = files?.[0]
    if (!picked) return
    if (!TYPES.includes(picked.type)) {
      onValidationError('Please choose a JPEG, PNG or WebP photo of your crop.')
      return
    }
    if (picked.size > MAX_BYTES) {
      onValidationError('That photo is too large. Please upload an image under 8 MB.')
      return
    }
    onSelect(picked)
  }

  return (
    <section className="card p-5 sm:p-6">
      <h2 className="text-lg font-bold text-leaf-900">Upload Crop Photo</h2>
      <p className="mt-1 text-sm text-leaf-700">
        Drag &amp; drop an image here or browse from your device.
      </p>

      {!preview ? (
        <div
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragging(false)
            handleFiles(e.dataTransfer.files)
          }}
          className={[
            'mt-5 flex flex-col items-center gap-4 rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-colors',
            dragging ? 'border-leaf-500 bg-leaf-50' : 'border-leaf-200 bg-leaf-50/50',
          ].join(' ')}
        >
          <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white text-leaf-600 shadow-card">
            <UploadCloud className="h-8 w-8" aria-hidden="true" />
          </span>
          <div>
            <p className="text-base font-semibold text-leaf-900">Drop your crop photo here</p>
            <p className="mt-1 text-sm text-leaf-600">
              Supported formats: JPEG, PNG, WebP (up to 8 MB)
            </p>
          </div>
          <button type="button" onClick={() => inputRef.current?.click()} className="btn-primary">
            <ImagePlus className="h-4 w-4" aria-hidden="true" />
            Browse Photo
          </button>
        </div>
      ) : (
        <div className="mt-5">
          <div className="overflow-hidden rounded-2xl border border-leaf-100 bg-leaf-900/5">
            <img
              src={preview}
              alt="Preview of the crop photo you uploaded"
              className="max-h-80 w-full object-contain"
            />
          </div>
          <p className="mt-3 truncate text-xs text-leaf-600">{file?.name}</p>

          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <button type="button" onClick={onAnalyze} disabled={analyzing} className="btn-primary flex-1 sm:flex-none">
              {analyzing ? <Spinner /> : <UploadCloud className="h-4 w-4" aria-hidden="true" />}
              {analyzing ? 'Analyzing...' : 'Analyze Crop'}
            </button>
            <button
              type="button"
              onClick={onClear}
              disabled={analyzing}
              className="btn-secondary flex-1 sm:flex-none"
            >
              <Trash2 className="h-4 w-4" aria-hidden="true" />
              Remove Image
            </button>
          </div>
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/webp"
        className="hidden"
        onChange={(e) => {
          handleFiles(e.target.files)
          e.target.value = ''
        }}
      />
    </section>
  )
}
