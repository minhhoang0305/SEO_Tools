import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { BarChart3, History, LogOut, Rocket, SearchCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import ThreeBackground from './ThreeBackground';

export default function AppShell({ children }) {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const variant = location.pathname.includes('submit') ? 'submit' : 'audit';

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="app-frame">
      <ThreeBackground variant={variant} />
      <header className="topbar">
        <button className="brand-mark" type="button" onClick={() => navigate('/seo-audit')}>
          <span className="brand-orbit"><SearchCheck size={20} /></span>
          <span>
            <strong>SEO Command</strong>
            <small>Audit and submission workspace</small>
          </span>
        </button>

        <nav className="nav-pills" aria-label="Primary navigation">
          <NavLink end to="/seo-audit" className={({ isActive }) => `nav-pill ${isActive ? 'active' : ''}`}>
            <BarChart3 size={16} />
            SEO Audit
          </NavLink>
          <NavLink to="/seo-audit/history" className={({ isActive }) => `nav-pill ${isActive ? 'active' : ''}`}>
            <History size={16} />
            Audit History
          </NavLink>
          <NavLink
            end
            to="/submit-website"
            className={({ isActive }) => {
              const isPlatformDetail = location.pathname.startsWith('/submit-website/') && location.pathname !== '/submit-website/history';
              return `nav-pill ${isActive || isPlatformDetail ? 'active' : ''}`;
            }}
          >
            <Rocket size={16} />
            Submit Platforms
          </NavLink>
          <NavLink to="/submit-website/history" className={({ isActive }) => `nav-pill ${isActive ? 'active' : ''}`}>
            <History size={16} />
            Submit History
          </NavLink>
        </nav>

        <div className="user-chip">
          <span className="avatar-mini">
            {(currentUser?.displayName || currentUser?.email || 'U').slice(0, 2).toUpperCase()}
          </span>
          <span className="user-chip-text">
            <strong>{currentUser?.displayName || 'SEO Manager'}</strong>
            <small>{currentUser?.email}</small>
          </span>
          <button className="icon-button danger" type="button" onClick={handleLogout} title="Đăng xuất">
            <LogOut size={16} />
          </button>
        </div>
      </header>

      <main className="app-main">{children}</main>
    </div>
  );
}
