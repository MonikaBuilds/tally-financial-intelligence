import { useState } from 'react'
import { useFetch } from '../hooks/useFetch'
import { apiGet } from '../api/client'
import PageHeader from '../components/layout/PageHeader'
import Loader from '../components/common/Loader'
import ErrorMessage from '../components/common/ErrorMessage'
import Card from '../components/common/Card'
import StatusPill from '../components/common/StatusPill'
import DataTable from '../components/common/DataTable'

const COMPANY_COLUMNS = [{ key: 'name', label: 'Company Name' }]

function TallyStatus() {
  const { data: status, loading, error } = useFetch('/tally/status')

  const [companies, setCompanies] = useState(null)
  const [companiesLoading, setCompaniesLoading] = useState(false)

  async function handleFetchCompanies() {
    setCompaniesLoading(true)
    setCompanies(null)

    try {
      const result = await apiGet('/tally/companies')
      setCompanies(result)
    } catch (err) {
      setCompanies({ success: false, error: err.message })
    } finally {
      setCompaniesLoading(false)
    }
  }

  return (
    <>
      <PageHeader title="Tally Status" />

      <Card title="Connection">
        {loading && <Loader />}
        {error && <ErrorMessage message={error} />}
        {status && (
          <>
            <StatusPill status={status.connected ? 'connected' : 'disconnected'} />
            <p className="card-note">{status.message}</p>
            {status.error && <p className="card-note">{status.error}</p>}
          </>
        )}
      </Card>

      <Card title="Companies">
        <button
          className="btn"
          onClick={handleFetchCompanies}
          disabled={companiesLoading}
        >
          {companiesLoading ? 'Fetching...' : 'Fetch Companies from Tally'}
        </button>

        {companies && companies.success && (
          <div style={{ marginTop: 16 }}>
            <DataTable columns={COMPANY_COLUMNS} rows={companies.companies} />
          </div>
        )}

        {companies && !companies.success && (
          <ErrorMessage message={companies.error || companies.message} />
        )}
      </Card>
    </>
  )
}

export default TallyStatus
