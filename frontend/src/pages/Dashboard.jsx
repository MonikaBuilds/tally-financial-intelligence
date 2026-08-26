import { useFetch } from '../hooks/useFetch'
import PageHeader from '../components/layout/PageHeader'
import Loader from '../components/common/Loader'
import ErrorMessage from '../components/common/ErrorMessage'
import StatCard from '../components/common/StatCard'

function Dashboard() {
  const { data: response, loading, error } = useFetch('/dashboard/summary')

  if (loading) return <Loader />
  if (error) return <ErrorMessage message={error} />
  if (!response.success) return <ErrorMessage message={response.error || response.message} />

  const summary = response.data

  return (
    <>
      <PageHeader title="Dashboard" subtitle="Live from Tally" />

      <div className="stat-grid">
        <StatCard label="Revenue" value={summary.revenue} tone="positive" />
        <StatCard label="Expenses" value={summary.expenses} tone="negative" />
        <StatCard label="Net Profit" value={summary.net_profit} tone="positive" />
        <StatCard label="Receivables" value={summary.receivables} />
        <StatCard label="Payables" value={summary.payables} />
        <StatCard label="Pending Invoices" value={summary.pending_invoices} format="number" />
      </div>
    </>
  )
}

export default Dashboard
