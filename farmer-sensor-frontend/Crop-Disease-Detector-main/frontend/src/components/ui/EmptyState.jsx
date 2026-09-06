export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center gap-3 px-6 py-14 text-center">
      {Icon && (
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-leaf-100 text-leaf-600">
          <Icon className="h-7 w-7" aria-hidden="true" />
        </span>
      )}
      <h3 className="text-lg font-semibold text-leaf-900">{title}</h3>
      {description && <p className="max-w-sm text-sm text-leaf-700">{description}</p>}
      {action}
    </div>
  )
}
