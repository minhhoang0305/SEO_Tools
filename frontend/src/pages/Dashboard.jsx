import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, Mail, ShieldCheck, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      setError('');
      setLoading(true);
      await logout();
      navigate('/login');
    } catch (err) {
      console.error(err);
      setError('Đã xảy ra lỗi khi đăng xuất.');
    } finally {
      setLoading(false);
    }
  }

  // Lấy chữ cái đầu của tên hiển thị để làm Avatar placeholder
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
  };

  return (
    <div className="dashboard-card">
      <div className="auth-header">
        <div className="badge">
          <ShieldCheck size={14} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
          Đã xác thực
        </div>
        <h1 className="auth-title" style={{ marginTop: '1rem' }}>Bảng Điều Khiển</h1>
        <p className="auth-subtitle">Chào mừng bạn đã truy cập khu vực bảo mật</p>
      </div>

      {error && (
        <div className="alert alert-error" style={{ width: '100%' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="user-profile">
        {currentUser?.photoURL ? (
          <img
            src={currentUser.photoURL}
            alt="Profile Avatar"
            className="avatar"
            referrerPolicy="no-referrer"
          />
        ) : (
          <div className="avatar-placeholder">
            {getInitials(currentUser?.displayName || currentUser?.email)}
          </div>
        )}
      </div>

      <div className="profile-info">
        <h2 className="profile-name">{currentUser?.displayName || 'Thành viên mới'}</h2>
        <div className="profile-email">
          <Mail size={16} />
          {currentUser?.email}
        </div>
      </div>

      <div style={{ width: '100%', borderTop: '1px solid var(--border-glass)', padding: '1.5rem 0 0 0' }}>
        <button
          disabled={loading}
          onClick={handleLogout}
          className="btn btn-outline"
          style={{ borderColor: 'rgba(239, 68, 68, 0.2)', color: 'hsl(var(--accent-error))' }}
        >
          {loading ? (
            <div className="spinner"></div>
          ) : (
            <>
              <LogOut size={18} />
              Đăng Xuất
            </>
          )}
        </button>
      </div>
    </div>
  );
}
