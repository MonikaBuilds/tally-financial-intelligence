import { useState } from 'react'
import { NavLink, useLocation } from 'react-router'
import ChatIcon from '../common/ChatIcon'
import { ALL_REPORTS, REPORT_ROUTES } from '../../reportsConfig'

const TOP_LINKS = [{ to: '/', label: 'Dashboard', end: true }]
const BOTTOM_LINKS = [{ to: '/tally-status', label: 'Tally Status' }]

function Sidebar() {
  const location = useLocation()
  const reportsActive = REPORT_ROUTES.some((path) => location.pathname === path)
  const [reportsOpen, setReportsOpen] = useState(reportsActive || true)

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">Tally Financial Intelligence</div>
      <nav className="sidebar-nav">
        {TOP_LINKS.map((link) => (
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

        <NavLink to="/chatbot" className={({ isActive }) => isActive ? 'sidebar-link sidebar-link--active' : 'sidebar-link'}>
          <ChatIcon size={16} className="sidebar-link-icon" />
          AI Assistant
        </NavLink>

        <button
          type="button"
          className={
            'sidebar-link sidebar-group-toggle' +
            (reportsActive ? ' sidebar-link--active' : '')
          }
          onClick={() => setReportsOpen((open) => !open)}
          aria-expanded={reportsOpen}
        >
          <span>Reports</span>
          <span className={`sidebar-chevron ${reportsOpen ? 'sidebar-chevron--open' : ''}`}>
            ▸
          </span>
        </button>

        {reportsOpen && (
          <div className="sidebar-group">
            {ALL_REPORTS.map((report) => (
              <NavLink
                key={report.to}
                to={report.to}
                className={({ isActive }) =>
                  isActive
                    ? 'sidebar-link sidebar-link--sub sidebar-link--active'
                    : 'sidebar-link sidebar-link--sub'
                }
              >
                {report.label}
              </NavLink>
            ))}
          </div>
        )}

        {BOTTOM_LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
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