export function formatCurrency(value) {
  if (value === undefined || value === null) return '-'

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatNumber(value) {
  if (value === undefined || value === null) return '-'

  return new Intl.NumberFormat('en-IN').format(value)
}
