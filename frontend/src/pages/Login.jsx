import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, LogIn, AlertCircle } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();

    if (!email || !password) {
      return setError('Vui lòng nhập đầy đủ Email và Mật khẩu.');
    }

    try {
      setError('');
      setLoading(true);
      await login(email, password);
      navigate('/');
    } catch (err) {
      console.error(err);
      if (err.code === 'auth/user-not-found' || err.code === 'auth/wrong-password' || err.code === 'auth/invalid-credential') {
        setError('Email hoặc mật khẩu không chính xác.');
      } else if (err.code === 'auth/invalid-email') {
        setError('Địa chỉ email không đúng định dạng.');
      } else {
        setError('Đã xảy ra lỗi khi đăng nhập.');
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSignIn() {
    try {
      setError('');
      setLoading(true);
      await loginWithGoogle();
      navigate('/');
    } catch (err) {
      console.error(err);
      setError('Đã xảy ra lỗi khi đăng nhập bằng Google.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-header">
        <h1 className="auth-title">Đăng Nhập</h1>
        <p className="auth-subtitle">Chào mừng bạn quay trở lại</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="email">Địa chỉ Email</label>
          <div className="input-wrapper">
            <input
              type="email"
              id="email"
              className="form-input"
              placeholder="example@domain.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Mail className="input-icon" size={18} />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="password">Mật khẩu</label>
          <div className="input-wrapper">
            <input
              type="password"
              id="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Lock className="input-icon" size={18} />
          </div>
        </div>

        <button disabled={loading} className="btn btn-primary" type="submit">
          {loading ? (
            <div className="spinner"></div>
          ) : (
            <>
              <LogIn size={18} />
              Đăng Nhập
            </>
          )}
        </button>
      </form>

      <div className="divider">Hoặc tiếp tục với</div>

      <button
        disabled={loading}
        onClick={handleGoogleSignIn}
        className="btn btn-outline"
        type="button"
      >
        <svg
          className="google-icon"
          style={{ marginRight: '8px' }}
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            fill="#4285F4"
          />
          <path
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            fill="#34A853"
          />
          <path
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
            fill="#FBBC05"
          />
          <path
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
            fill="#EA4335"
          />
        </svg>
        Google
      </button>

      <div className="auth-footer">
        Chưa có tài khoản?
        <Link to="/register" className="auth-link">Đăng ký ngay</Link>
      </div>
    </div>
  );
}
