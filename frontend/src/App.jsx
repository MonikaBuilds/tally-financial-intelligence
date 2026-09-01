import { Routes, Route } from 'react-router'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Ledger from './pages/Ledger'
import ProfitLoss from './pages/ProfitLoss'
import Receivables from './pages/Receivables'
import Payables from './pages/Payables'
import PendingInvoices from './pages/PendingInvoices'
import TrialBalance from './pages/TrialBalance'
import BalanceSheet from './pages/BalanceSheet'
import TallyStatus from './pages/TallyStatus'
import Chatbot from './pages/Chatbot'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/ledger" element={<Ledger />} />
        <Route path="/profit-loss" element={<ProfitLoss />} />
        <Route path="/receivables" element={<Receivables />} />
        <Route path="/payables" element={<Payables />} />
        <Route path="/pending-invoices" element={<PendingInvoices />} />
        <Route path="/trial-balance" element={<TrialBalance />} />
        <Route path="/balance-sheet" element={<BalanceSheet />} />
        <Route path="/tally-status" element={<TallyStatus />} />
        <Route path="/chatbot" element={<Chatbot />} />
      </Route>
    </Routes>
  )
}

export default App