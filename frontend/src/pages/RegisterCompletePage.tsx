import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { User, Lock, Eye, EyeOff, Loader2, AlertCircle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function RegisterCompletePage() {
  const { completeRegistration } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('sessionId');

  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState({ score: 0, text: 'Rất yếu', color: '#ef4444' });

  // Realtime password strength calculation
  useEffect(() => {
    if (!password) {
      setPasswordStrength({ score: 0, text: 'Rất yếu', color: '#ef4444' });
      return;
    }

    let score = 0;
    if (password.length >= 6) score += 1;
    if (password.length >= 10) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    let text = 'Rất yếu';
    let color = '#ef4444'; // red

    if (score >= 4) {
      text = 'Rất mạnh';
      color = '#10b981'; // green
    } else if (score >= 3) {
      text = 'Mạnh';
      color = '#10b981'; // green
    } else if (score >= 2) {
      text = 'Trung bình';
      color = '#f59e0b'; // amber
    }

    setPasswordStrength({ score, text, color });
  }, [password]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!sessionId) {
      setError('Mã phiên đăng ký (sessionId) không hợp lệ hoặc đã hết hạn.');
      return;
    }

    if (!name.trim()) {
      setError('Vui lòng nhập họ tên của bạn.');
      return;
    }

    if (password.length < 6) {
      setError('Mật khẩu phải có ít nhất 6 ký tự.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Mật khẩu xác nhận không khớp.');
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      await completeRegistration(sessionId, name, password);
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err: any) {
      setError(err?.message || 'Không thể hoàn tất đăng ký. Vui lòng kiểm tra lại đường dẫn email.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!sessionId) {
    return (
      <div className="auth-page-container">
        <div className="auth-background-decor">
          <div className="decor-circle circle-1"></div>
          <div className="decor-circle circle-2"></div>
        </div>

        <div className="auth-card-wrapper">
          <div className="auth-card auth-error-card">
            <div className="success-icon-wrapper error-icon-wrapper">
              <ShieldAlert size={48} className="success-icon error-icon" />
            </div>
            <h1>Phiên đăng ký không hợp lệ</h1>
            <p>
              Đường dẫn xác thực này không có mã phiên hoặc mã đã hết hạn. Vui lòng đăng ký lại để nhận liên kết mới.
            </p>
            <Link to="/register" className="auth-submit-button text-center no-underline">
              <span>Đăng ký lại</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page-container">
      <div className="auth-background-decor">
        <div className="decor-circle circle-1"></div>
        <div className="decor-circle circle-2"></div>
      </div>

      <div className="auth-card-wrapper">
        <div className="auth-card">
          {success ? (
            <div className="auth-success-step">
              <div className="success-icon-wrapper">
                <CheckCircle2 size={48} className="success-icon" />
              </div>
              <h1>Đăng ký thành công!</h1>
              <p className="success-description">
                Tài khoản của bạn đã được thiết lập thành công. Hệ thống đang tự động chuyển hướng bạn đến trang đăng nhập trong giây lát...
              </p>
              <div className="auth-loader-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          ) : (
            <>
              <div className="auth-header">
                <div className="auth-brand">
                  <span className="auth-brand-mark">ST</span>
                  <span className="auth-brand-text">SEO Tools</span>
                </div>
                <h1>Hoàn tất tài khoản</h1>
                <p>Email đã được xác thực thành công. Vui lòng thiết lập hồ sơ để hoàn thành.</p>
              </div>

              {error && (
                <div className="auth-error-alert" role="alert">
                  <AlertCircle size={18} className="flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="auth-form">
                <div className="auth-input-group">
                  <label htmlFor="name">Họ và tên</label>
                  <div className="auth-input-wrapper">
                    <span className="auth-input-icon">
                      <User size={18} />
                    </span>
                    <input
                      id="name"
                      type="text"
                      placeholder="Nguyễn Văn A"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <div className="auth-input-group">
                  <label htmlFor="password">Mật khẩu</label>
                  <div className="auth-input-wrapper">
                    <span className="auth-input-icon">
                      <Lock size={18} />
                    </span>
                    <input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={isSubmitting}
                      required
                    />
                    <button
                      type="button"
                      className="auth-password-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? 'Ẩn mật khẩu' : 'Hiển thị mật khẩu'}
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  {password && (
                    <div className="password-strength-container">
                      <div className="password-strength-bars">
                        {[1, 2, 3, 4, 5].map((idx) => (
                          <div
                            key={idx}
                            className={`strength-bar ${idx <= passwordStrength.score ? 'active' : ''}`}
                            style={{
                              backgroundColor: idx <= passwordStrength.score ? passwordStrength.color : undefined
                            }}
                          ></div>
                        ))}
                      </div>
                      <span className="password-strength-text" style={{ color: passwordStrength.color }}>
                        Độ mạnh: {passwordStrength.text}
                      </span>
                    </div>
                  )}
                </div>

                <div className="auth-input-group">
                  <label htmlFor="confirmPassword">Xác nhận mật khẩu</label>
                  <div className="auth-input-wrapper">
                    <span className="auth-input-icon">
                      <Lock size={18} />
                    </span>
                    <input
                      id="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      disabled={isSubmitting}
                      required
                    />
                    <button
                      type="button"
                      className="auth-password-toggle"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      aria-label={showConfirmPassword ? 'Ẩn mật khẩu' : 'Hiển thị mật khẩu'}
                    >
                      {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>

                <button type="submit" className="auth-submit-button" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      <span>Đang tạo tài khoản...</span>
                    </>
                  ) : (
                    <span>Hoàn tất đăng ký</span>
                  )}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
