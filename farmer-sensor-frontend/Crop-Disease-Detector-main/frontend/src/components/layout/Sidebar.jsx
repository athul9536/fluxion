import { NavLink } from 'react-router-dom'
import Brand from './Brand'
import { NAV_ITEMS } from './navItems'

const linkClass = ({ isActive }) =>
  [
    'flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-colors',
    isActive
      ? 'bg-leaf-600 text-white shadow-card'
      : 'text-leaf-700 hover:bg-leaf-100 hover:text-leaf-900',
  ].join(' ')

export function SidebarNav({ onNavigate }) {
  return (
    <nav className="flex flex-col gap-1" aria-label="Main navigation">
      {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink key={to} to={to} end={to === '/'} className={linkClass} onClick={onNavigate}>
          <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}

export function FarmerBadge() {
  return (
    <div className="rounded-xl border border-leaf-100 bg-leaf-50 px-4 py-3">
      <div className="flex items-center gap-2">
        <span className="relative flex h-2.5 w-2.5">
          <span className="absolute inline-flex h-full w-full rounded-full bg-leaf-400 opacity-70" />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-leaf-500" />
        </span>
        <p className="text-sm font-semibold text-leaf-900">Premium Farmer</p>
      </div>
      <p className="mt-0.5 pl-[18px] text-xs text-leaf-600">Online</p>
    </div>
  )
}

export default function Sidebar() {
  return (
    <aside className="hidden w-72 shrink-0 border-r border-leaf-100 bg-white/85 backdrop-blur lg:flex lg:flex-col">
      <div className="px-6 py-6">
        <Brand />
      </div>
      <div className="flex-1 overflow-y-auto px-4">
        <SidebarNav />
      </div>
      <div className="p-4">
        <FarmerBadge />
      </div>
    </aside>
  )
}
