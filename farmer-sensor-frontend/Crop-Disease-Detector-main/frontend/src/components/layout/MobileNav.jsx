import { Menu, X } from 'lucide-react'
import { useEffect } from 'react'
import Brand from './Brand'
import { FarmerBadge, SidebarNav } from './Sidebar'

export default function MobileNav({ open, onOpen, onClose }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <>
      <header className="sticky top-0 z-30 flex items-center justify-between border-b border-leaf-100 bg-white/95 px-4 py-3 backdrop-blur lg:hidden">
        <Brand compact />
        <button
          type="button"
          onClick={onOpen}
          className="flex h-11 w-11 items-center justify-center rounded-xl border border-leaf-200 text-leaf-700"
          aria-label="Open navigation menu"
          aria-expanded={open}
        >
          <Menu className="h-5 w-5" aria-hidden="true" />
        </button>
      </header>

      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 h-full w-full bg-leaf-900/40"
            onClick={onClose}
            aria-label="Close navigation menu"
          />
          <div className="absolute left-0 top-0 flex h-full w-[82%] max-w-xs flex-col bg-white shadow-lift">
            <div className="flex items-center justify-between px-5 py-4">
              <Brand />
              <button
                type="button"
                onClick={onClose}
                className="flex h-10 w-10 items-center justify-center rounded-xl text-leaf-700 hover:bg-leaf-100"
                aria-label="Close navigation menu"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto px-3">
              <SidebarNav onNavigate={onClose} />
            </div>
            <div className="p-4">
              <FarmerBadge />
            </div>
          </div>
        </div>
      )}
    </>
  )
}
