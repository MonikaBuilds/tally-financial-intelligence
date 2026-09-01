import { useMemo, useState } from 'react'
import { useFetch } from '../hooks/useFetch'
import PageHeader from '../components/layout/PageHeader'
import Loader from '../components/common/Loader'
import ErrorMessage from '../components/common/ErrorMessage'
import Card from '../components/common/Card'
import DataTable from '../components/common/DataTable'
import ExportButtons from '../components/common/ExportButtons'
import { formatCurrency } from '../utils/format'

// Tally shows ledger balances with a Dr/Cr suffix rather than a +/- sign.
function formatBalance(value) {
  if (value === undefined || value === null) return '-'
  if (value === 0) return formatCurrency(0)
  const suffix = value < 0 ? 'Cr' : 'Dr'
  return `${formatCurrency(Math.abs(value))} ${suffix}`
}

const COLUMNS = [
  { key: 'date', label: 'Date' },
  { key: 'particulars', label: 'Particulars' },
  { key: 'voucher_type', label: 'Vch Type' },
  { key: 'voucher_number', label: 'Vch No.' },
  { key: 'debit', label: 'Debit', render: (row) => (row.debit ? formatCurrency(row.debit) : '') },
  { key: 'credit', label: 'Credit', render: (row) => (row.credit ? formatCurrency(row.credit) : '') },
  { key: 'running_balance', label: 'Balance', render: (row) => formatBalance(row.running_balance) },
]

function Ledger() {
  const { data: listResponse, loading: listLoading, error: listError } = useFetch('/reports/ledgers')
  const ledgers = listResponse?.success ? listResponse.ledgers : []

  const [ledgerName, setLedgerName] = useState('')
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [selectionError, setSelectionError] = useState(null)
  const [activeLedger, setActiveLedger] = useState(null) // { name, from, to }

  const queryPath = useMemo(() => {
    if (!activeLedger) return null

    const params = new URLSearchParams({ ledger_name: activeLedger.name })
    if (activeLedger.from) params.set('from_date', activeLedger.from)
    if (activeLedger.to) params.set('to_date', activeLedger.to)

    return `/reports/ledger?${params.toString()}`
  }, [activeLedger])

  const { data: reportResponse, loading: reportLoading, error: reportError } = useFetch(queryPath)

  function handleViewStatement(event) {
    event.preventDefault()

    const trimmed = ledgerName.trim()
    const match = ledgers.find((ledger) => ledger.name.toLowerCase() === trimmed.toLowerCase())

    if (!match) {
      setSelectionError('Pick a ledger from the suggestions list before viewing its statement.')
      return
    }

    if (fromDate && toDate && fromDate > toDate) {
      setSelectionError('From date cannot be later than to date.')
      return
    }

    setSelectionError(null)
    setActiveLedger({ name: match.name, from: fromDate || null, to: toDate || null })
  }

  const report = reportResponse?.success ? reportResponse.report : null

  const rows = report
    ? [
        {
          date: '',
          particulars: 'Opening Balance',
          voucher_type: '',
          voucher_number: '',
          debit: report.opening_balance > 0 ? report.opening_balance : 0,
          credit: report.opening_balance < 0 ? Math.abs(report.opening_balance) : 0,
          running_balance: report.opening_balance,
        },
        ...report.entries,
      ]
    : []

  const totalDebit = report ? report.entries.reduce((sum, row) => sum + (row.debit || 0), 0) : 0
  const totalCredit = report ? report.entries.reduce((sum, row) => sum + (row.credit || 0), 0) : 0

  return (
    <>
      <PageHeader title="Ledger" subtitle="View any ledger's statement in Tally's format and export it" />

      <Card title="Select Ledger">
        {listLoading && <Loader />}
        {listError && <ErrorMessage message={listError} />}

        {!listLoading && !listError && (
          <form className="ledger-filters" onSubmit={handleViewStatement}>
            <div className="form-field">
              <label htmlFor="ledger-search">Ledger</label>
              <input
                id="ledger-search"
                list="ledger-options"
                value={ledgerName}
                onChange={(event) => setLedgerName(event.target.value)}
                placeholder="Search ledger, e.g. Cash, ABC Traders"
                autoComplete="off"
              />
              <datalist id="ledger-options">
                {ledgers.map((ledger) => (
                  <option key={ledger.name} value={ledger.name} />
                ))}
              </datalist>
            </div>

            <div className="form-field form-field--date">
              <label htmlFor="ledger-from">From Date</label>
              <input
                id="ledger-from"
                type="date"
                value={fromDate}
                onChange={(event) => setFromDate(event.target.value)}
              />
            </div>

            <div className="form-field form-field--date">
              <label htmlFor="ledger-to">To Date</label>
              <input
                id="ledger-to"
                type="date"
                value={toDate}
                onChange={(event) => setToDate(event.target.value)}
              />
            </div>

            <button type="submit" className="btn">View Statement</button>
          </form>
        )}

        {selectionError && <p className="selection-error">{selectionError}</p>}
      </Card>

      {!activeLedger && (
        <Card>
          <p className="empty-state">Select a ledger above and click "View Statement" to see its statement.</p>
        </Card>
      )}

      {activeLedger && reportLoading && <Loader />}
      {activeLedger && reportError && <ErrorMessage message={reportError} />}
      {activeLedger && reportResponse && !reportResponse.success && (
        <ErrorMessage message={reportResponse.error || reportResponse.message} />
      )}

      {report && (
        <Card
          title={`Ledger: ${report.ledger_name}`}
        >
          <p className="card-note ledger-summary-note">
            Period: {activeLedger.from || 'books beginning'} to {activeLedger.to || 'today'}
            {' · '}Opening Balance: {formatBalance(report.opening_balance)}
          </p>

          <div style={{ marginBottom: 16 }}>
            <ExportButtons
              basePath="/reports/ledger/export"
              params={{
                ledger_name: activeLedger.name,
                from_date: activeLedger.from || undefined,
                to_date: activeLedger.to || undefined,
              }}
              filenameBase={`${activeLedger.name.trim().replace(/\s+/g, '_').replace(/\//g, '-')}_ledger`}
            />
          </div>

          <DataTable columns={COLUMNS} rows={rows} />

          <div className="table-footer">
            <span>Total Debit: {formatCurrency(totalDebit)}</span>
            <span>Total Credit: {formatCurrency(totalCredit)}</span>
            <span>Closing Balance: {formatBalance(report.closing_balance)}</span>
          </div>
        </Card>
      )}
    </>
  )
}

export default Ledger