import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LogOut, Mail, ShieldCheck, AlertCircle, Search, 
  Globe, Flag, Languages, RefreshCw, FileText, CheckCircle2, 
  AlertTriangle, Info, ArrowLeft, ArrowRight, ExternalLink, Calendar, Key
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5001';

const getStatusLabel = (status) => {
  if (status === 0 || status === 'Pending') return 'Đang chờ';
  if (status === 1 || status === 'Processing') return 'Đang phân tích';
  if (status === 2 || status === 'Completed') return 'Đã hoàn thành';
  if (status === 3 || status === 'Failed') return 'Thất bại';
  return String(status ?? 'Thất bại');
};

const getStatusClass = (status) => {
  if (status === 0 || status === 'Pending') return 'pending';
  if (status === 1 || status === 'Processing') return 'processing';
  if (status === 2 || status === 'Completed') return 'completed';
  if (status === 3 || status === 'Failed') return 'failed';
  
  if (typeof status === 'string') {
    return status.toLowerCase();
  }
  return 'failed';
};

export default function Dashboard() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  // Audit form states
  const [url, setUrl] = useState('');
  const [keyword, setKeyword] = useState('');
  const [country, setCountry] = useState('vn');
  const [language, setLanguage] = useState('vi');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');

  // Audits list & details states
  const [audits, setAudits] = useState([]);
  const [isLoadingList, setIsLoadingList] = useState(true);
  const [listError, setListError] = useState('');
  const [selectedAuditId, setSelectedAuditId] = useState(null);
  const [auditDetails, setAuditDetails] = useState(null);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [detailsError, setDetailsError] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Polling ref
  const pollingIntervalRef = useRef(null);

  // Fetch audits list
  const fetchAudits = async (showRefreshedState = false) => {
    if (showRefreshedState) setIsRefreshing(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/audits`, {
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      });
      if (!response.ok) throw new Error('Không thể tải danh sách kết quả crawl.');
      const data = await response.json();
      setAudits(data);
      setListError('');
    } catch (err) {
      console.error(err);
      setListError('Đã xảy ra lỗi khi tải danh sách kết quả.');
    } finally {
      setIsLoadingList(false);
      setIsRefreshing(false);
    }
  };

  // Fetch single audit details
  const fetchAuditDetails = async (id, isSilent = false) => {
    if (!isSilent) setIsLoadingDetails(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/audits/${id}`, {
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      });
      if (!response.ok) throw new Error('Không thể tải chi tiết kết quả crawl.');
      const data = await response.json();
      setAuditDetails(data);
      setDetailsError('');
    } catch (err) {
      console.error(err);
      setDetailsError('Không thể tải chi tiết kết quả audit này.');
    } finally {
      if (!isSilent) setIsLoadingDetails(false);
    }
  };

  // Logout handler
  async function handleLogout() {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error(err);
    }
  }

  // Submit crawl request
  const handleSubmitCrawl = async (e) => {
    e.preventDefault();
    setFormError('');
    setFormSuccess('');

    if (!url) return setFormError('Vui lòng nhập URL cần crawl.');
    if (!keyword) return setFormError('Vui lòng nhập từ khóa cần tối ưu.');

    // Simple URL validation
    try {
      new URL(url);
    } catch (_) {
      return setFormError('URL không hợp lệ. Vui lòng nhập đầy đủ định dạng (ví dụ: https://example.com).');
    }

    setIsSubmitting(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/audits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken}`
        },
        body: JSON.stringify({
          url,
          keyword,
          country,
          language
        })
      });

      if (!response.ok) throw new Error('Yêu cầu crawl thất bại. Vui lòng thử lại.');
      const data = await response.json();
      
      setFormSuccess('Gửi yêu cầu crawl thành công! Đang xử lý...');
      setUrl('');
      setKeyword('');
      
      // Select the new audit and fetch lists
      fetchAudits();
      if (data.auditId) {
        setSelectedAuditId(data.auditId);
        fetchAuditDetails(data.auditId);
      }
    } catch (err) {
      setFormError(err.message || 'Có lỗi xảy ra khi tạo yêu cầu crawl.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchAudits();
  }, []);

  // Poll status of pending/processing audits
  useEffect(() => {
    // If there is any pending or processing audit, setup interval
    const hasUnfinishedAudits = audits.some(
      a => a.status === 'Pending' || a.status === 'Processing' || a.status === 0 || a.status === 1
    );

    const isCurrentAuditUnfinished = auditDetails && 
      (auditDetails.status === 'Pending' || auditDetails.status === 'Processing' || auditDetails.status === 0 || auditDetails.status === 1);

    if (hasUnfinishedAudits || isCurrentAuditUnfinished) {
      pollingIntervalRef.current = setInterval(() => {
        fetchAudits();
        if (selectedAuditId) {
          fetchAuditDetails(selectedAuditId, true);
        }
      }, 4000);
    } else {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    }

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [audits, selectedAuditId, auditDetails]);

  // Fetch details when selected audit changes
  useEffect(() => {
    if (selectedAuditId) {
      fetchAuditDetails(selectedAuditId);
    } else {
      setAuditDetails(null);
    }
  }, [selectedAuditId]);

  // Score circular indicator builder
  const renderScoreCircle = (score, label, colorClass) => {
    const radius = 35;
    const stroke = 6;
    const normalizedRadius = radius - stroke;
    const circumference = normalizedRadius * 2 * Math.PI;
    const strokeDashoffset = circumference - (Math.min(100, Math.max(0, score)) / 100) * circumference;

    return (
      <div className={`score-card ${colorClass}`}>
        <div className="circle-progress-container">
          <svg height="90" width="90">
            <circle
              className="circle-bg"
              r={normalizedRadius}
              cx="45"
              cy="45"
            />
            <circle
              className="circle-val"
              strokeDasharray={circumference + ' ' + circumference}
              style={{ strokeDashoffset }}
              r={normalizedRadius}
              cx="45"
              cy="45"
              stroke={colorClass === 'seo' ? 'url(#seoGradient)' : colorClass === 'tech' ? '#3b82f6' : '#10b981'}
            />
            <defs>
              <linearGradient id="seoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="hsl(var(--accent-primary))" />
                <stop offset="100%" stopColor="hsl(var(--accent-secondary))" />
              </linearGradient>
            </defs>
          </svg>
          <div className="circle-text">{score}</div>
        </div>
        <div className="score-label">{label}</div>
      </div>
    );
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
  };

  return (
    <div className="dashboard-grid">
      {/* SIDEBAR PANEL: User Profile & New Crawl Form */}
      <div className="dashboard-panel">
        {/* Profile Card */}
        <div className="sidebar-profile">
          {currentUser?.photoURL ? (
            <img
              src={currentUser.photoURL}
              alt="Profile"
              className="sidebar-avatar"
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className="sidebar-avatar-placeholder">
              {getInitials(currentUser?.displayName || currentUser?.email)}
            </div>
          )}
          <div className="sidebar-info">
            <div className="sidebar-name">{currentUser?.displayName || 'Thành viên mới'}</div>
            <div className="sidebar-email">{currentUser?.email}</div>
          </div>
          <button 
            onClick={handleLogout} 
            className="refresh-btn" 
            title="Đăng xuất"
            style={{ color: 'hsl(var(--accent-error))' }}
          >
            <LogOut size={18} />
          </button>
        </div>

        {/* Start New Audit */}
        <div>
          <h2 className="form-title">Crawl & Audit Website</h2>
          <p className="auth-subtitle" style={{ fontSize: '0.85rem', marginBottom: '1.25rem' }}>
            Phân tích điểm SEO và phát hiện các lỗi tối ưu hóa của trang web
          </p>

          <form onSubmit={handleSubmitCrawl} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {formError && (
              <div className="alert alert-error" style={{ padding: '0.6rem 0.8rem', marginBottom: 0 }}>
                <AlertCircle size={16} />
                <span style={{ fontSize: '0.8rem' }}>{formError}</span>
              </div>
            )}
            {formSuccess && (
              <div className="alert alert-success" style={{ padding: '0.6rem 0.8rem', marginBottom: 0 }}>
                <CheckCircle2 size={16} />
                <span style={{ fontSize: '0.8rem' }}>{formSuccess}</span>
              </div>
            )}

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Địa chỉ website (URL)</label>
              <div className="input-wrapper">
                <Globe size={18} className="input-icon" />
                <input
                  type="text"
                  placeholder="https://example.com/bai-viet"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="form-input"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Từ khóa SEO mục tiêu</label>
              <div className="input-wrapper">
                <Key size={18} className="input-icon" />
                <input
                  type="text"
                  placeholder="ví dụ: thiết kế web chuẩn SEO"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  className="form-input"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Quốc gia</label>
                <div className="select-wrapper">
                  <Flag size={18} className="input-icon" />
                  <select 
                    value={country} 
                    onChange={(e) => setCountry(e.target.value)}
                    className="form-select"
                    disabled={isSubmitting}
                  >
                    <option value="vn">Việt Nam</option>
                    <option value="us">Hoa Kỳ</option>
                    <option value="jp">Nhật Bản</option>
                    <option value="sg">Singapore</option>
                  </select>
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Ngôn ngữ</label>
                <div className="select-wrapper">
                  <Languages size={18} className="input-icon" />
                  <select 
                    value={language} 
                    onChange={(e) => setLanguage(e.target.value)}
                    className="form-select"
                    disabled={isSubmitting}
                  >
                    <option value="vi">Tiếng Việt</option>
                    <option value="en">English</option>
                    <option value="ja">日本語</option>
                  </select>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary"
              style={{ marginTop: '0.5rem' }}
            >
              {isSubmitting ? (
                <div className="spinner"></div>
              ) : (
                <>
                  <Search size={18} />
                  Bắt Đầu Phân Tích
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* MAIN PANEL: Audit List OR Selected Audit Details */}
      <div className="dashboard-panel scrollable-panel" style={{ minHeight: '550px' }}>
        {selectedAuditId ? (
          /* AUDIT DETAILS VIEW */
          <div>
            <div className="detail-header">
              <button 
                onClick={() => setSelectedAuditId(null)}
                className="btn btn-outline"
                style={{ width: 'auto', padding: '0.5rem 1rem', display: 'inline-flex', marginBottom: '1.25rem' }}
              >
                <ArrowLeft size={16} />
                Quay lại danh sách
              </button>

              {isLoadingDetails ? (
                <div className="loading-screen" style={{ minHeight: '200px' }}>
                  <div className="loading-dots">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                  <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.9rem' }}>Đang tải chi tiết kết quả...</p>
                </div>
              ) : detailsError ? (
                <div className="alert alert-error">
                  <AlertCircle size={18} />
                  <span>{detailsError}</span>
                </div>
              ) : auditDetails ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <div>
                      <h1 className="detail-title">{auditDetails.keyword}</h1>
                      <a 
                        href={auditDetails.url} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        style={{ color: 'hsl(var(--accent-primary))', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.9rem' }}
                      >
                        {auditDetails.url}
                        <ExternalLink size={14} />
                      </a>
                    </div>
                    <div className={`status-badge ${getStatusClass(auditDetails.status)}`}>
                      {getStatusLabel(auditDetails.status)}
                    </div>
                  </div>

                  <div className="audit-item-meta" style={{ marginTop: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Calendar size={14} />
                      <span>Bắt đầu lúc: {new Date(auditDetails.createdAt).toLocaleString('vi-VN')}</span>
                    </div>
                    {auditDetails.completedAt && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <CheckCircle2 size={14} style={{ color: '#4ade80' }} />
                        <span>Hoàn thành lúc: {new Date(auditDetails.completedAt).toLocaleString('vi-VN')}</span>
                      </div>
                    )}
                    <div>
                      <span>Quốc gia: {auditDetails.country?.toUpperCase()}</span>
                    </div>
                    <div>
                      <span>Ngôn ngữ: {auditDetails.language?.toUpperCase()}</span>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>

            {/* Audit Content (Scores & Issues) */}
            {!isLoadingDetails && auditDetails && (
              <div>
                {auditDetails.status === 'Pending' || auditDetails.status === 'Processing' || auditDetails.status === 0 || auditDetails.status === 1 ? (
                  <div style={{ textAlign: 'center', padding: '4rem 2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.5rem' }}>
                    <div className="spinner" style={{ width: '40px', height: '40px', borderWidth: '4px', borderTopColor: 'hsl(var(--accent-primary))' }}></div>
                    <div>
                      <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Hệ thống đang thu thập và phân tích dữ liệu SEO</h3>
                      <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.9rem' }}>Kết quả sẽ tự động hiển thị sau ít giây...</p>
                    </div>
                  </div>
                ) : auditDetails.status === 'Failed' || auditDetails.status === 3 ? (
                  <div style={{ textAlign: 'center', padding: '4rem 2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
                    <AlertCircle size={48} style={{ color: 'hsl(var(--accent-error))' }} />
                    <div>
                      <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Phân tích SEO thất bại</h3>
                      <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.9rem' }}>Đã xảy ra sự cố trong quá trình crawl website. Vui lòng kiểm tra lại URL hoặc thử lại sau.</p>
                    </div>
                  </div>
                ) : auditDetails.report ? (
                  /* Completed state showing report */
                  <div>
                    {/* Score gauges */}
                    <div className="scores-container">
                      {renderScoreCircle(auditDetails.report.seoScore, 'Điểm SEO tổng thể', 'seo')}
                      {renderScoreCircle(auditDetails.report.technicalScore, 'Tối ưu kỹ thuật', 'tech')}
                      {renderScoreCircle(auditDetails.report.onPageScore, 'Tối ưu On-Page', 'onpage')}
                    </div>

                    {/* Issues breakdown */}
                    <div>
                      <h3 className="issues-section-title">
                        <FileText size={18} />
                        Danh sách vấn đề cần cải thiện ({auditDetails.report.issues?.length || 0})
                      </h3>

                      {!auditDetails.report.issues || auditDetails.report.issues.length === 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem', padding: '3rem', background: 'rgba(34, 197, 94, 0.05)', borderRadius: '16px', border: '1px solid rgba(34, 197, 94, 0.15)', textAlign: 'center' }}>
                          <CheckCircle2 size={36} style={{ color: '#4ade80' }} />
                          <h4 style={{ color: '#4ade80', fontSize: '1.1rem' }}>Website của bạn thật tuyệt vời!</h4>
                          <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.9rem' }}>Không tìm thấy lỗi SEO quan trọng nào cần khắc phục.</p>
                        </div>
                      ) : (
                        <div className="issues-container">
                          {auditDetails.report.issues.map((issue) => {
                            const severityLower = issue.severity?.toLowerCase() || 'info';
                            const isHigh = severityLower === 'high' || severityLower === 'critical';
                            const isMedium = severityLower === 'medium' || severityLower === 'warning';
                            
                            const severityClass = isHigh ? 'critical' : isMedium ? 'warning' : 'info';
                            const severityLabel = isHigh ? 'Nghiêm trọng' : isMedium ? 'Cảnh báo' : 'Thông tin';

                            // Fallback descriptions and recommendations in case they are missing from DB
                            let description = issue.description;
                            let recommendation = issue.recommendation;

                            if (!description || !recommendation) {
                              const titleLower = issue.title?.toLowerCase() || '';
                              if (titleLower.includes('robots.txt')) {
                                description = description || 'Tệp robots.txt không tồn tại trên website.';
                                recommendation = recommendation || 'Tạo tệp robots.txt ở thư mục gốc của website để hướng dẫn các bot tìm kiếm.';
                              } else if (titleLower.includes('sitemap.xml')) {
                                description = description || 'Sơ đồ trang web sitemap.xml không được tìm thấy.';
                                recommendation = recommendation || 'Tạo tệp sitemap.xml chứa danh sách URL của trang web và khai báo trong robots.txt hoặc Google Search Console.';
                              } else if (titleLower.includes('redirect chain') || titleLower.includes('redirect')) {
                                description = description || 'Có quá nhiều bước chuyển hướng (redirect) trước khi tải được trang.';
                                recommendation = recommendation || 'Giảm số lượng chuyển hướng trung gian để cải thiện tốc độ tải trang và SEO.';
                              } else if (titleLower.includes('open graph') || titleLower.includes('og:')) {
                                description = description || 'Thiếu các thẻ Open Graph (og:title, og:description, hoặc og:image) dùng để hiển thị khi chia sẻ trên mạng xã hội.';
                                recommendation = recommendation || 'Thêm đầy đủ các thẻ meta Open Graph vào phần <head>.';
                              } else if (titleLower.includes('twitter')) {
                                description = description || 'Thiếu thẻ meta Twitter Card cho mạng xã hội Twitter.';
                                recommendation = recommendation || 'Thêm thẻ <meta name="twitter:card" content="summary_large_image"> vào phần <head>.';
                              } else if (titleLower.includes('title tag') || titleLower.includes('missing title') || titleLower.includes('title is')) {
                                description = description || 'Thẻ tiêu đề <title> bị thiếu hoặc chưa tối ưu trong phần head.';
                                recommendation = recommendation || 'Thêm hoặc cập nhật thẻ <title> chứa từ khóa mục tiêu với độ dài từ 30 đến 65 ký tự.';
                              } else if (titleLower.includes('meta description')) {
                                description = description || 'Thẻ mô tả (meta description) bị thiếu hoặc chưa tối ưu.';
                                recommendation = recommendation || 'Thêm hoặc cập nhật thẻ <meta name="description" content="..."> với độ dài từ 120 đến 160 ký tự.';
                              } else if (titleLower.includes('h1')) {
                                description = description || 'Thẻ tiêu đề chính H1 bị thiếu hoặc có nhiều hơn một thẻ.';
                                recommendation = recommendation || 'Sử dụng duy nhất một thẻ H1 chứa từ khóa chính cho mỗi trang.';
                              } else if (titleLower.includes('image') || titleLower.includes('alt')) {
                                description = description || 'Một số hình ảnh trên trang thiếu thuộc tính alt (văn bản thay thế).';
                                recommendation = recommendation || 'Bổ sung thuộc tính alt vào tất cả các thẻ <img> để tối ưu hóa SEO hình ảnh.';
                              }
                            }

                            return (
                              <div key={issue.id} className="issue-card">
                                <div className="issue-header">
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    {isHigh ? (
                                      <AlertCircle size={18} style={{ color: '#ef4444' }} />
                                    ) : isMedium ? (
                                      <AlertTriangle size={18} style={{ color: '#f59e0b' }} />
                                    ) : (
                                      <Info size={18} style={{ color: '#3b82f6' }} />
                                    )}
                                    <span className="issue-title">{issue.title}</span>
                                  </div>
                                  <span className={`severity-pill ${severityClass}`}>
                                    {severityLabel}
                                  </span>
                                </div>

                                {description && <p className="issue-description">{description}</p>}

                                {recommendation && (
                                  <div className="recommendation-box">
                                    <div className="recommendation-title">Khuyến nghị khắc phục:</div>
                                    <div className="recommendation-text">{recommendation}</div>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
                    <p style={{ color: 'hsl(var(--text-secondary))' }}>Không tìm thấy báo cáo kết quả cho đợt crawl này.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          /* AUDITS HISTORY LIST VIEW */
          <div>
            <div className="audit-list-header">
              <h2 className="audit-list-title">Lịch Sử Phân Tích</h2>
              <button 
                onClick={() => fetchAudits(true)} 
                disabled={isRefreshing}
                className="refresh-btn"
                title="Tải lại danh sách"
              >
                <RefreshCw size={16} className={isRefreshing ? 'spinner' : ''} />
              </button>
            </div>

            {isLoadingList ? (
              <div className="loading-screen" style={{ minHeight: '300px' }}>
                <div className="loading-dots">
                  <div className="dot"></div>
                  <div className="dot"></div>
                  <div className="dot"></div>
                </div>
                <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.9rem' }}>Đang tải lịch sử crawl...</p>
              </div>
            ) : listError ? (
              <div className="alert alert-error">
                <AlertCircle size={18} />
                <span>{listError}</span>
              </div>
            ) : audits.length === 0 ? (
              <div className="detail-placeholder">
                <Globe size={48} style={{ color: 'hsl(var(--text-muted))' }} />
                <h3>Chưa có lịch sử phân tích</h3>
                <p style={{ fontSize: '0.9rem', maxWidth: '350px' }}>Hãy nhập địa chỉ trang web và từ khóa ở bảng bên trái để thực hiện đợt phân tích SEO đầu tiên của bạn.</p>
              </div>
            ) : (
              <div className="audit-items-container">
                {audits.map((audit) => (
                  <div 
                    key={audit.id} 
                    onClick={() => setSelectedAuditId(audit.id)}
                    className="audit-item-card"
                  >
                    <div className="audit-item-info">
                      <div className="audit-item-url">{audit.url}</div>
                      <div className="audit-item-meta">
                        <span style={{ color: '#fff', fontWeight: 500 }}>Từ khóa: {audit.keyword}</span>
                        <span>•</span>
                        <span>{new Date(audit.createdAt).toLocaleString('vi-VN')}</span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span className={`status-badge ${getStatusClass(audit.status)}`}>
                        {getStatusLabel(audit.status)}
                      </span>
                      <ArrowRight size={16} style={{ color: 'hsl(var(--text-muted))' }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
