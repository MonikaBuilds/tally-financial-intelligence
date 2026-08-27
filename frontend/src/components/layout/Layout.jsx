import { Outlet, Link, useLocation } from 'react-router'
import Sidebar from './Sidebar'
import ChatIcon from '../common/ChatIcon'

function Layout() {
  const location = useLocation()
  const onChatPage = location.pathname === '/chatbot'

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="app-content">
        <Outlet />
      </main>

      {!onChatPage && (
        <Link to="/chatbot" className="chat-fab" aria-label="Open AI Assistant">
          <ChatIcon size={24} />
        </Link>
      )}
    </div>
  )
}

export default Layout