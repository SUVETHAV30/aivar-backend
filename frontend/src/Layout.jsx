import { NavLink } from 'react-router-dom';

const NAV = [
  { to: '/',          icon: '⬡', label: 'Dashboard'  },
  { to: '/agents',    icon: '🤖', label: 'Agents'     },
  { to: '/baselines', icon: '📐', label: 'Baselines'  },
  { to: '/sessions',  icon: '📡', label: 'Sessions'   },
  { to: '/alerts',    icon: '🔔', label: 'Alerts'     },
  { to: '/drift',     icon: '📈', label: 'Drift'      },
];

const ROLE_COLOR = {
  admin:   'var(--cyan)',
  analyst: 'var(--purple)',
  viewer:  'var(--text-muted)',
};

export default function Layout({ children, role, onLogout }) {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="logo-tag">AI Agent Monitor</div>
          <h2>Behavioral Baseline Builder</h2>
        </div>
        <nav className="sidebar-nav">
          {NAV.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon">{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div style={{ marginBottom: 8 }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Signed in as </span>
            <span style={{ fontSize: 12, fontWeight: 600, color: ROLE_COLOR[role] || 'var(--cyan)' }}>
              {role?.toUpperCase()}
            </span>
          </div>
          <button
            className="btn btn-ghost"
            style={{ padding: '6px 12px', fontSize: 12, width: '100%' }}
            onClick={onLogout}
          >
            🚪 Sign Out
          </button>
          <div style={{ marginTop: 8, color: 'var(--text-muted)', fontSize: 10 }}>v1.0.0 · Phase 11</div>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
