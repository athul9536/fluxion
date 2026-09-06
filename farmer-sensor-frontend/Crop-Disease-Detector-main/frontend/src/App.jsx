import { Route, Routes } from 'react-router-dom'
import DashboardLayout from './components/layout/DashboardLayout'
import AiAssistant from './pages/AiAssistant'
import DashboardHome from './pages/DashboardHome'
import DiseaseDetection from './pages/DiseaseDetection'
import Location from './pages/Location'
import MyReports from './pages/MyReports'
import NotFound from './pages/NotFound'
import Settings from './pages/Settings'

export default function App() {
  return (
    <DashboardLayout>
      <Routes>
        <Route path="/" element={<DashboardHome />} />
        <Route path="/detect" element={<DiseaseDetection />} />
        <Route path="/assistant" element={<AiAssistant />} />
        <Route path="/reports" element={<MyReports />} />
        <Route path="/location" element={<Location />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </DashboardLayout>
  )
}
