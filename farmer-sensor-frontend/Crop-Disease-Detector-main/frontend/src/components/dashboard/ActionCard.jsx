import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function ActionCard({ icon: Icon, title, description, cta, to, accent = 'leaf' }) {
  const accents = {
    leaf: 'bg-leaf-100 text-leaf-700',
    sky: 'bg-sky-100 text-sky-700',
  }

  return (
    <article className="card group flex flex-col p-6 transition-shadow hover:shadow-lift">
      <span className={`flex h-12 w-12 items-center justify-center rounded-2xl ${accents[accent]}`}>
        <Icon className="h-6 w-6" aria-hidden="true" />
      </span>
      <h3 className="mt-5 text-xl font-bold text-leaf-900">{title}</h3>
      <p className="mt-2 flex-1 text-sm leading-relaxed text-leaf-700">{description}</p>
      <Link to={to} className="btn-primary mt-6 w-full sm:w-auto sm:self-start">
        {cta}
        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
      </Link>
    </article>
  )
}
