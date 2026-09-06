import { Check, Info, MapPin, Save, Trash2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useDashboard } from '../context/DashboardContext'

export default function Location() {
  const { farmLocation } = useDashboard()
  const [address, setAddress] = useState('')
  const [pincode, setPincode] = useState('')
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState(null)

  // Hydrate once the stored value has loaded.
  useEffect(() => {
    setAddress(farmLocation.location.address || '')
    setPincode(farmLocation.location.pincode || '')
  }, [farmLocation.location.address, farmLocation.location.pincode])

  const submit = (e) => {
    e.preventDefault()
    setError(null)
    if (pincode && pincode.length !== 6) {
      setError('A pincode should be 6 digits. Please check and try again.')
      return
    }
    farmLocation.save({ address, pincode })
    setSaved(true)
    window.setTimeout(() => setSaved(false), 2500)
  }

  const reset = () => {
    farmLocation.clear()
    setAddress('')
    setPincode('')
    setError(null)
  }

  return (
    <div className="space-y-6">
      <header>
        <p className="flex items-center gap-2 text-sm font-semibold text-leaf-600">
          <MapPin className="h-4 w-4" aria-hidden="true" />
          Your Farm
        </p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-leaf-900 sm:text-4xl">
          Location
        </h1>
        <p className="mt-2 max-w-xl text-base text-leaf-700">
          Add your farm address and pincode. When a disease is detected, the pincode is
          saved with the report so outbreaks can be tracked by area.
        </p>
      </header>

      <form onSubmit={submit} className="card p-5 sm:p-6">
        <div className="space-y-5">
          <div>
            <label htmlFor="farm-address" className="block text-sm font-semibold text-leaf-900">
              Address
            </label>
            <p className="mt-0.5 text-xs text-leaf-600">
              Kept on this device for your reference only.
            </p>
            <textarea
              id="farm-address"
              rows={3}
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="House name, village, panchayat, district"
              className="mt-2 w-full resize-none rounded-xl border border-leaf-200 bg-white px-4 py-3 text-sm text-leaf-900 placeholder:text-leaf-400 focus:border-leaf-500"
            />
          </div>

          <div>
            <label htmlFor="farm-pincode" className="block text-sm font-semibold text-leaf-900">
              Pin Code
            </label>
            <p className="mt-0.5 text-xs text-leaf-600">
              6 digits. Saved with a report only when a disease is found.
            </p>
            <input
              id="farm-pincode"
              type="text"
              inputMode="numeric"
              autoComplete="postal-code"
              maxLength={6}
              value={pincode}
              onChange={(e) => setPincode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="688001"
              aria-describedby={error ? 'pincode-error' : undefined}
              aria-invalid={Boolean(error)}
              className="mt-2 w-full max-w-[12rem] rounded-xl border border-leaf-200 bg-white px-4 py-3 text-sm tabular-nums text-leaf-900 placeholder:text-leaf-400 focus:border-leaf-500 sm:max-w-[14rem]"
            />
            {error && (
              <p id="pincode-error" className="mt-2 text-xs font-medium text-amber-700" role="alert">
                {error}
              </p>
            )}
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center">
          <button type="submit" className="btn-primary w-full sm:w-auto">
            {saved ? (
              <Check className="h-4 w-4" aria-hidden="true" />
            ) : (
              <Save className="h-4 w-4" aria-hidden="true" />
            )}
            {saved ? 'Saved' : 'Save Location'}
          </button>
          {(farmLocation.location.address || farmLocation.location.pincode) && (
            <button type="button" onClick={reset} className="btn-secondary w-full sm:w-auto">
              <Trash2 className="h-4 w-4" aria-hidden="true" />
              Clear
            </button>
          )}
        </div>

        <p aria-live="polite" className="sr-only">
          {saved ? 'Location saved.' : ''}
        </p>
      </form>

      <div className="card flex items-start gap-3 p-5">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-sky-100 text-sky-700">
          <Info className="h-4 w-4" aria-hidden="true" />
        </span>
        <div className="text-sm leading-relaxed text-leaf-700">
          <p className="font-semibold text-leaf-900">How this is used</p>
          <p className="mt-1">
            Your pincode is attached to a detection report only when the AI finds a disease.
            Healthy scans are saved without it. The address never leaves this device.
          </p>
        </div>
      </div>
    </div>
  )
}
