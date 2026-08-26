import { formatCurrency, formatNumber } from '../../utils/format'

function StatCard({ label, value, tone = 'default', format = 'currency' }) {
  const displayValue = format === 'number' ? formatNumber(value) : formatCurrency(value)

  return (
    <div className={`stat-card stat-card--${tone}`}>
      <span className="stat-card-label">{label}</span>
      <span className="stat-card-value">{displayValue}</span>
    </div>
  )
}

export default StatCard
