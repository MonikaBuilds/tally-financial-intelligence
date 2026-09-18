import { Link } from 'react-router'
import PageHeader from '../components/layout/PageHeader'
import Card from '../components/common/Card'
import { ALL_REPORTS } from '../reportsConfig'

function ReportsIndex() {
  return (
    <div className="reports-index">
      <PageHeader
        title="Reports"
        subtitle="Every report in one place — pick one to view, or export it as PDF / Excel."
      />

      <div className="reports-grid">
        {ALL_REPORTS.map((report) => (
          <Link key={report.to} to={report.to} className="report-card">
            <Card>
              <div className="report-card-title">{report.label}</div>
              <div className="report-card-desc">{report.description}</div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default ReportsIndex