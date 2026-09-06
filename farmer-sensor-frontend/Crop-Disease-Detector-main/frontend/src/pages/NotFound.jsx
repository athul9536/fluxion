import { Sprout } from 'lucide-react'
import { Link } from 'react-router-dom'
import EmptyState from '../components/ui/EmptyState'

export default function NotFound() {
  return (
    <div className="card">
      <EmptyState
        icon={Sprout}
        title="Page not found"
        description="That page doesn't exist. Head back to your dashboard to keep going."
        action={
          <Link to="/" className="btn-primary mt-2">
            Back to Dashboard
          </Link>
        }
      />
    </div>
  )
}
