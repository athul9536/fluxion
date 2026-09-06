import {
  FileText,
  LayoutDashboard,
  MapPin,
  MessageSquareText,
  ScanLine,
  Settings,
} from 'lucide-react'

export const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/detect', label: 'Disease Detection', icon: ScanLine },
  { to: '/assistant', label: 'AI Assistant', icon: MessageSquareText },
  { to: '/reports', label: 'My Reports', icon: FileText },
  { to: '/location', label: 'Location', icon: MapPin },
  { to: '/settings', label: 'Settings', icon: Settings },
]
