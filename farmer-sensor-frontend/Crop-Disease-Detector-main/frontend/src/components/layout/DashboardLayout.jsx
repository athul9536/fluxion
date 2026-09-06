import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import MobileNav from './MobileNav'
import Sidebar from './Sidebar'

export default function DashboardLayout({ children }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const { pathname } = useLocation()
  const isChat = pathname === '/assistant'

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <MobileNav open={menuOpen} onOpen={() => setMenuOpen(true)} onClose={() => setMenuOpen(false)} />
        <main
          className={
            isChat
              ? 'flex min-h-0 flex-1 flex-col px-4 py-4 sm:px-6 lg:px-8 lg:py-6'
              : 'flex-1 px-4 py-6 sm:px-6 lg:px-10 lg:py-8'
          }
        >
          <div className={isChat ? 'mx-auto flex w-full max-w-4xl flex-1 flex-col' : 'mx-auto w-full max-w-6xl'}>
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
