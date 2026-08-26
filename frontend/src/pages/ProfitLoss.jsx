import { useFetch } from '../hooks/useFetch'
import PageHeader from '../components/layout/PageHeader'
import Loader from '../components/common/Loader'
import ErrorMessage from '../components/common/ErrorMessage'
import Card from '../components/common/Card'
import DataTable from '../components/common/DataTable'
import { formatCurrency } from '../utils/format'

const COLUMNS = [
  { key: 'name', label: 'Account' },
  { key: 'main_amount', label: 'Amount', render: (row) => formatCurrency(row.main_amount) },
  { key: 'sub_amount', label: 'Sub Amount', render: (row) => formatCurrency(row.sub_amount) },
]

function ProfitLoss() {
  const { data: response, loading, error } = useFetch('/reports/profit-loss')

  if (loading) return <Loader />
  if (error) return <ErrorMessage message={error} />
  if (!response.success) return <ErrorMessage message={response.error || response.message} />

  return (
    <>
      <PageHeader title="Profit & Loss" />

      <Card>
        <DataTable columns={COLUMNS} rows={response.report} />
      </Card>
    </>
  )
}

export default ProfitLoss
