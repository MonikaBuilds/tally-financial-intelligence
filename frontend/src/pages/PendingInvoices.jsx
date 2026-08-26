import { useFetch } from '../hooks/useFetch'
import PageHeader from '../components/layout/PageHeader'
import Loader from '../components/common/Loader'
import ErrorMessage from '../components/common/ErrorMessage'
import Card from '../components/common/Card'
import DataTable from '../components/common/DataTable'
import StatusPill from '../components/common/StatusPill'
import { formatCurrency } from '../utils/format'

const COLUMNS = [
  { key: 'party', label: 'Party' },
  { key: 'bill_reference', label: 'Bill Reference' },
  { key: 'bill_date', label: 'Bill Date' },
  { key: 'type', label: 'Type', render: (row) => <StatusPill status={row.type} /> },
  {
    key: 'outstanding_amount',
    label: 'Outstanding',
    render: (row) => formatCurrency(row.outstanding_amount),
  },
  { key: 'status', label: 'Status', render: (row) => <StatusPill status={row.status} /> },
]

function PendingInvoices() {
  const { data: response, loading, error } = useFetch('/reports/pending-invoices')

  if (loading) return <Loader />
  if (error) return <ErrorMessage message={error} />
  if (!response.success) return <ErrorMessage message={response.error || response.message} />

  return (
    <>
      <PageHeader title="Pending Invoices" />

      <Card>
        <DataTable columns={COLUMNS} rows={response.data.invoices} />
      </Card>
    </>
  )
}

export default PendingInvoices
