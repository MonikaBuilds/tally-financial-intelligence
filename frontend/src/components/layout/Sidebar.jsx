import { NavLink } from 'react-router'

const NAV_LINKS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/profit-loss', label: 'Profit & Loss' },
  { to: '/receivables', label: 'Receivables' },
  { to: '/payables', label: 'Payables' },
  { to: '/pending-invoices', label: 'Pending Invoices' },
  { to: '/trial-balance', label: 'Trial Balance' },
  { to: '/balance-sheet', label: 'Balance Sheet' },
  { to: '/tally-status', label: 'Tally Status' },
]

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">Tally Financial Intelligence</div>
      <nav className="sidebar-nav">
        {NAV_LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              isActive ? 'sidebar-link sidebar-link--active' : 'sidebar-link'
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
