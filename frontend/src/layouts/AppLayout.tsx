import { Activity, BarChart3, FolderKanban, LogOut } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { to: '/', label: 'Dashboard', icon: BarChart3 },
  { to: '/projects', label: 'Projects', icon: FolderKanban },
  { to: '/audits', label: 'Audits', icon: Activity },
];

export function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-main">
          <div className="brand">
            <span className="brand-mark">ST</span>
            <span>SEO Tools</span>
          </div>

          <nav className="nav-list" aria-label="Main navigation">
            {navItems.map((item) => {
              const Icon = item.icon;

              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    isActive ? 'nav-link active' : 'nav-link'
                  }
                >
                  <Icon size={18} aria-hidden="true" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {user && (
          <div className="sidebar-footer">
            <div className="user-info-card">
              <span className="user-name">{user.name}</span>
              <span className="user-email" title={user.email}>{user.email}</span>
            </div>
            <button className="logout-button" type="button" onClick={logout}>
              <LogOut size={16} aria-hidden="true" />
              <span>Đăng xuất</span>
            </button>
          </div>
        )}
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
