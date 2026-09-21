import { useState } from 'react'
import { NavLink, useLocation } from 'react-router'
import ChatIcon from '../common/ChatIcon'
import { ALL_REPORTS, REPORT_ROUTES } from '../../reportsConfig'

const NAV_LINKS = [
  {
    to: '/',
    label: 'Dashboard',
    end: true,
  },
  {
    to: '/chatbot',
    label: 'AI Assistant',
    icon: true,
  },
  {
    to: '/ledger',
    label: 'Ledger',
  },
  {
    to: '/profit-loss',
    label: 'Profit & Loss',
  },
  {
    to: '/receivables',
    label: 'Receivables',
  },
  {
    to: '/payables',
    label: 'Payables',
  },
  {
    to: '/pending-invoices',
    label: 'Pending Invoices',
  },
  {
    to: '/trial-balance',
    label: 'Trial Balance',
  },
  {
    to: '/balance-sheet',
    label: 'Balance Sheet',
  },
  {
    to: '/tally-status',
    label: 'Tally Status',
  },
  {
    to: '/admin/users',
    label: 'User Management',
  },
]

function getCurrentUser() {
  try {
    const storedUser = sessionStorage.getItem('chat_user')

    if (!storedUser) {
      return null
    }

    return JSON.parse(storedUser)
  } catch {
    return null
  }
}

function getInitial(username) {
  if (!username) {
    return 'U'
  }

  return username
    .trim()
    .charAt(0)
    .toUpperCase()
}

function Sidebar({ onLogout }) {
  const user = getCurrentUser()

  const companies = Array.isArray(user?.companies)
    ? user.companies
    : []

  const companyLabel =
    companies.length === 1
      ? companies[0]
      : companies.length > 1
        ? `${companies.length} companies`
        : 'No company'

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-logo">
          TF
        </div>

        <div className="sidebar-brand-copy">
          <strong>
            Tally Financial
          </strong>

          <span>
            Intelligence
          </span>
        </div>
      </div>

      <div className="sidebar-company">
        <span className="sidebar-section-label">
          Company
        </span>

        <div className="sidebar-company-value">
          <span className="company-indicator" />

          <span title={companyLabel}>
            {companyLabel}
          </span>
        </div>
      </div>

      <nav
        className="sidebar-nav"
        aria-label="Main navigation"
      >
        <span className="sidebar-section-label">
          Workspace
        </span>

        {NAV_LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              isActive
                ? 'sidebar-link sidebar-link--active'
                : 'sidebar-link'
            }
          >
            {link.icon && (
              <ChatIcon
                size={16}
                className="sidebar-link-icon"
              />
            )}

            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-account">
        <div className="sidebar-user">
          <div className="sidebar-avatar">
            {getInitial(user?.username)}
          </div>

          <div className="sidebar-user-info">
            <strong title={user?.username}>
              {user?.username || 'User'}
            </strong>

            <span>
              Authorized user
            </span>
          </div>
        </div>

        <button
          type="button"
          className="sidebar-logout"
          onClick={onLogout}
        >
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              d="M10 5H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h4"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            />

            <path
              d="M14 8l4 4-4 4M18 12H9"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>

          <span>
            Sign out
          </span>
        </button>
      </div>
    </aside>
  )
}

export default Sidebar