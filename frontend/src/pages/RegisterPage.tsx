import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Loader2, AlertCircle, Inbox, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

type RegisterStep = 'input' | 'success';

export function RegisterPage() {
  const { register } = useAuth();

  const [email, setEmail] = useState('');
  const [step, setStep] = useState<RegisterStep>('input');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      setError('Vui lòng nhập địa chỉ email.');
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      await register(email);
      setStep('success');
    } catch (err: any) {
      setError(err?.message || 'Có lỗi xảy ra trong quá trình đăng ký. Vui lòng thử lại.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page-container">
      <div className="auth-background-decor">
        <div className="decor-circle circle-1"></div>
        <div className="decor-circle circle-2"></div>
      </div>

      <div className="auth-card-wrapper">
        <div className="auth-card">
          {step === 'input' ? (
            <>
              <div className="auth-header">
                <div className="auth-brand">
                  <span className="auth-brand-mark">ST</span>
                  <span className="auth-brand-text">SEO Tools</span>
                </div>
                <h1>Tạo tài khoản mới</h1>
                <p>Khởi đầu dễ dàng để tối ưu hóa hiệu quả SEO cho website của bạn.</p>
              </div>

              {error && (
                <div className="auth-error-alert" role="alert">
                  <AlertCircle size={18} className="flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="auth-form">
                <div className="auth-input-group">
                  <label htmlFor="email">Email</label>
                  <div className="auth-input-wrapper">
                    <span className="auth-input-icon">
                      <Mail size={18} />
                    </span>
                    <input
                      id="email"
                      type="email"
                      placeholder="name@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={isSubmitting}
                      required
                    />
                  </div>
                </div>

                <button type="submit" className="auth-submit-button" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      <span>Đang gửi email...</span>
                    </>
                  ) : (
                    <span>Gửi link xác thực</span>
                  )}
                </button>
              </form>

              <div className="auth-footer">
                <p>
                  Đã có tài khoản?{' '}
                  <Link to="/login" className="auth-link">
                    Đăng nhập
                  </Link>
                </p>
              </div>
            </>
          ) : (
            <div className="auth-success-step">
              <div className="success-icon-wrapper">
                <Inbox size={48} className="success-icon" />
              </div>
              <h1>Kiểm tra hòm thư của bạn</h1>
              <p className="success-description">
                Chúng tôi đã gửi một email xác nhận đến <strong>{email}</strong>. Vui lòng bấm vào liên kết trong email để xác minh tài khoản và tiếp tục.
              </p>
              <div className="success-guidelines">
                <h4>Không tìm thấy email?</h4>
                <ul>
                  <li>Kiểm tra hộp thư rác (Spam) hoặc quảng cáo.</li>
                  <li>Đảm bảo rằng bạn nhập đúng địa chỉ email.</li>
                </ul>
              </div>
              <button
                type="button"
                className="auth-secondary-button"
                onClick={() => setStep('input')}
              >
                <ArrowLeft size={16} />
                <span>Quay lại nhập email</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
