import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LogOut, Globe, Mail, ShieldCheck, AlertCircle, 
  CheckCircle2, RefreshCw, ArrowLeft, ArrowRight, ExternalLink, 
  Lock, ChevronDown, ChevronUp, FileText, Settings, Send
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5001';

export default function SubmitWebsite() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  // Core Form states
  const [url, setUrl] = useState('');
  const [siteName, setSiteName] = useState('');
  const [description, setDescription] = useState('');
  const [sitemapUrl, setSitemapUrl] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  
  // Platform settings
  const [platforms, setPlatforms] = useState([]);
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(true);
  const [activeSettingsPlatformId, setActiveSettingsPlatformId] = useState(null);
  const [connectSuccess, setConnectSuccess] = useState('');
  const [connectError, setConnectError] = useState('');
  const [isConnectingPlatform, setIsConnectingPlatform] = useState(false);
  const [sessionFile, setSessionFile] = useState(null);

  // Job Submission States
  const [isSubmittingJob, setIsSubmittingJob] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [submitSuccess, setSubmitSuccess] = useState('');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  // Jobs History & Details States
  const [jobs, setJobs] = useState([]);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const [jobsError, setJobsError] = useState('');
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const [isLoadingJobDetails, setIsLoadingJobDetails] = useState(false);
  const [jobDetailsError, setJobDetailsError] = useState('');
  const [isRefreshingHistory, setIsRefreshingHistory] = useState(false);

  // UI state
  const [expandedDetailId, setExpandedDetailId] = useState(null);

  // Polling ref
  const pollingIntervalRef = useRef(null);

  // Fetch active platforms
  const fetchPlatforms = async () => {
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/platforms`, {
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      });
      if (!response.ok) throw new Error('Không thể lấy danh sách platforms.');
      const data = await response.json();
      setPlatforms(data);
      
      // Auto-select all by default (backend uses camelCase: id)
      setSelectedPlatforms(data.map(p => p.id));
    } catch (err) {
      console.error(err);
      setSubmitError('Lỗi tải danh sách SEO platforms.');
    } finally {
      setIsLoadingPlatforms(false);
    }
  };

  // Fetch jobs history
  const fetchJobs = async (silent = false) => {
    if (!silent) setIsLoadingJobs(true);
    else setIsRefreshingHistory(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/history`, {
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      });
      if (!response.ok) throw new Error('Không thể tải lịch sử submit.');
      const data = await response.json();
      setJobs(data);
      setJobsError('');
    } catch (err) {
      console.error(err);
      setJobsError('Đã xảy ra lỗi khi tải danh sách lịch sử.');
    } finally {
      setIsLoadingJobs(false);
      setIsRefreshingHistory(false);
    }
  };

  // Fetch single job details (progress)
  const fetchJobDetails = async (id, silent = false) => {
    if (!silent) setIsLoadingJobDetails(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/jobs/${id}`, {
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      });
      if (!response.ok) throw new Error('Không thể tải chi tiết tiến trình.');
      const data = await response.json();
      setJobDetails(data);
      setJobDetailsError('');
    } catch (err) {
      console.error(err);
      setJobDetailsError('Lỗi khi tải chi tiết tiến trình submit.');
    } finally {
      if (!silent) setIsLoadingJobDetails(false);
    }
  };

  // Import locally generated StackShare session
  const handleImportPlatformSession = async (platformId) => {
    setConnectError('');
    setConnectSuccess('');
    setIsConnectingPlatform(true);

    if (!sessionFile) {
      setConnectError('Vui lòng chọn file stackshare_storage_state.json trước khi import.');
      setIsConnectingPlatform(false);
      return;
    }

    try {
      const credentialData = await sessionFile.text();
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken}`
        },
        body: JSON.stringify({
          platformId,
          credentialData
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.Message || 'Không thể import session.');
      }

      setConnectSuccess('Đã import session thành công. Docker sẽ dùng storage_state này cho Submit.');
      setSessionFile(null);

      setTimeout(() => {
        setConnectSuccess('');
        setActiveSettingsPlatformId(null);
      }, 2000);
    } catch (err) {
      setConnectError(err.message);
    } finally {
      setIsConnectingPlatform(false);
    }
  };

  // Submit website job
  const handleFormSubmit = (e) => {
    e.preventDefault();
    setSubmitError('');
    setSubmitSuccess('');

    if (!url) return setSubmitError('Vui lòng nhập URL website cần submit.');
    if (selectedPlatforms.length === 0) return setSubmitError('Vui lòng chọn ít nhất một Platform.');

    try {
      new URL(url);
    } catch (_) {
      return setSubmitError('Định dạng URL không hợp lệ (ví dụ: https://example.com).');
    }

    // Open confirmation dialog
    setShowConfirmDialog(true);
  };

  const executeSubmitJob = async () => {
    setShowConfirmDialog(false);
    setIsSubmittingJob(true);
    setSubmitError('');
    
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken}`
        },
        body: JSON.stringify({
          websiteUrl: url,
          platformIds: selectedPlatforms,
          siteName,
          description,
          sitemapUrl,
          contactEmail
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.Message || 'Gửi yêu cầu submit thất bại.');
      }
      
      const data = await response.json();
      setSubmitSuccess('Gửi yêu cầu thành công! Đang tiến hành submit bất đồng bộ...');
      
      // Reset form
      setUrl('');
      setSiteName('');
      setDescription('');
      setSitemapUrl('');
      setContactEmail('');
      
      fetchJobs(true);
      if (data.jobId) { // Backend returns jobId
        setSelectedJobId(data.jobId);
      }
    } catch (err) {
      setSubmitError(err.message);
    } finally {
      setIsSubmittingJob(false);
    }
  };

  // Toggle platform selection
  const handleSelectPlatform = (id) => {
    if (selectedPlatforms.includes(id)) {
      setSelectedPlatforms(selectedPlatforms.filter(p => p !== id));
    } else {
      setSelectedPlatforms([...selectedPlatforms, id]);
    }
  };

  const handleSelectAllPlatforms = () => {
    if (selectedPlatforms.length === platforms.length) {
      setSelectedPlatforms([]);
    } else {
      setSelectedPlatforms(platforms.map(p => p.id));
    }
  };

  // Initial Load
  useEffect(() => {
    fetchPlatforms();
    fetchJobs();
  }, []);

  // Poll status of running submit jobs
  useEffect(() => {
    const hasRunningJobs = jobs.some(j => j.status === 'Pending' || j.status === 'Running');
    const isCurrentJobRunning = jobDetails && (jobDetails.status === 'Pending' || jobDetails.status === 'Running');

    if (hasRunningJobs || isCurrentJobRunning) {
      pollingIntervalRef.current = setInterval(() => {
        fetchJobs(true);
        if (selectedJobId) {
          fetchJobDetails(selectedJobId, true);
        }
      }, 3000);
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
  }, [jobs, selectedJobId, jobDetails]);

  // Fetch job details on selection
  useEffect(() => {
    if (selectedJobId) {
      fetchJobDetails(selectedJobId);
    } else {
      setJobDetails(null);
    }
    setExpandedDetailId(null);
  }, [selectedJobId]);

  async function handleLogout() {
    try {
      await logout();
      navigate('/login');
    } catch (err) {
      console.error(err);
    }
  }

  const getStatusLabel = (status) => {
    switch (status) {
      case 'Pending': return 'Chờ hàng đợi';
      case 'Running': return 'Đang chạy';
      case 'Success': return 'Thành công';
      case 'Failed': return 'Thất bại';
      case 'Completed': return 'Hoàn thành';
      case 'RequiresManualAction': return 'Cần tương tác';
      default: return status;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'Pending': return 'pending';
      case 'Running': return 'processing';
      case 'Success':
      case 'Completed': return 'completed';
      case 'Failed': return 'failed';
      case 'RequiresManualAction': return 'warning';
      default: return 'failed';
    }
  };

  return (
    <div className="dashboard-grid">
      {/* LEFT PANEL: User profile, settings and submission form */}
      <div className="dashboard-panel">
        
        {/* Profile Section */}
        <div className="sidebar-profile">
          <div className="sidebar-avatar-placeholder">
            {currentUser?.email ? currentUser.email.substring(0, 2).toUpperCase() : 'US'}
          </div>
          <div className="sidebar-info">
            <div className="sidebar-name">{currentUser?.displayName || 'SEO Manager'}</div>
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

        {/* Feature Navigation Toggle */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <button 
            onClick={() => navigate('/')} 
            className="btn btn-outline" 
            style={{ flex: 1, padding: '0.5rem', fontSize: '0.8rem', display: 'flex', gap: '4px', justifyContent: 'center', alignItems: 'center' }}
          >
            <ArrowLeft size={14} /> Crawl & Audit SEO
          </button>
          <button 
            className="btn btn-primary" 
            style={{ flex: 1, padding: '0.5rem', fontSize: '0.8rem', cursor: 'default' }}
            disabled
          >
            Submit SEO Platforms
          </button>
        </div>

        {/* Submit Website Form */}
        <div>
          <h2 className="form-title">Submit Website to SEO Platforms</h2>
          <p className="auth-subtitle" style={{ fontSize: '0.82rem', marginBottom: '1.25rem' }}>
            Tự động submit và khai báo chỉ mục cho các platform công cụ tìm kiếm và danh mục.
          </p>

          <form onSubmit={handleFormSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {submitError && (
              <div className="alert alert-error" style={{ padding: '0.6rem 0.8rem', marginBottom: 0 }}>
                <AlertCircle size={16} />
                <span style={{ fontSize: '0.8rem' }}>{submitError}</span>
              </div>
            )}
            {submitSuccess && (
              <div className="alert alert-success" style={{ padding: '0.6rem 0.8rem', marginBottom: 0 }}>
                <CheckCircle2 size={16} />
                <span style={{ fontSize: '0.8rem' }}>{submitSuccess}</span>
              </div>
            )}

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Địa chỉ website cần submit (URL) *</label>
              <div className="input-wrapper">
                <Globe size={18} className="input-icon" />
                <input
                  type="text"
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="form-input"
                  required
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Tên website (Site Name)</label>
              <input
                type="text"
                placeholder="ví dụ: My SEO Portal"
                value={siteName}
                onChange={(e) => setSiteName(e.target.value)}
                className="form-input"
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Mô tả ngắn trang web</label>
              <textarea
                placeholder="Nhập mô tả giới thiệu về trang web..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="form-input"
                rows="2"
                style={{ resize: 'none' }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Contact Email</label>
                <input
                  type="email"
                  placeholder="admin@example.com"
                  value={contactEmail}
                  onChange={(e) => setContactEmail(e.target.value)}
                  className="form-input"
                />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="form-label">Sitemap URL</label>
                <input
                  type="text"
                  placeholder="sitemap.xml"
                  value={sitemapUrl}
                  onChange={(e) => setSitemapUrl(e.target.value)}
                  className="form-input"
                />
              </div>
            </div>

            {/* Platform selection list */}
            <div className="form-group" style={{ marginBottom: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <label className="form-label" style={{ marginBottom: 0 }}>Chọn Platform để submit</label>
                <button
                  type="button"
                  onClick={handleSelectAllPlatforms}
                  style={{ background: 'none', border: 'none', color: 'hsl(var(--accent-primary))', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 500 }}
                >
                  {selectedPlatforms.length === platforms.length ? 'Bỏ chọn tất cả' : 'Chọn tất cả'}
                </button>
              </div>

              {isLoadingPlatforms ? (
                <div style={{ padding: '0.5rem 0', color: 'hsl(var(--text-muted))', fontSize: '0.8rem' }}>Đang tải platforms...</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '0.75rem' }}>
                  {platforms.map(platform => (
                    <div key={platform.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', cursor: 'pointer', width: '80%' }}>
                        <input
                          type="checkbox"
                          checked={selectedPlatforms.includes(platform.id)}
                          onChange={() => handleSelectPlatform(platform.id)}
                          style={{ cursor: 'pointer' }}
                        />
                        <span>{platform.name}</span>
                        <span style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))' }}>
                          ({platform.submitMethod === 'API' ? 'HTTP Direct' : 'UI Automation'})
                        </span>
                      </label>

                      {/* Setup button for local session import if UI automation */}
                      {platform.submitMethod !== 'API' && (
                        <button
                          type="button"
                          onClick={() => {
                            setActiveSettingsPlatformId(
                              activeSettingsPlatformId === platform.id ? null : platform.id
                            );
                            setConnectSuccess('');
                            setConnectError('');
                          }}
                          className="refresh-btn"
                          title="Import Session"
                          style={{ padding: '2px' }}
                        >
                          <Settings size={14} style={{ color: activeSettingsPlatformId === platform.id ? 'hsl(var(--accent-primary))' : 'inherit' }} />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Popup Configuration Form if platform clicked */}
            {activeSettingsPlatformId && (
              <div style={{ background: 'rgba(59, 130, 246, 0.05)', border: '1px solid rgba(59, 130, 246, 0.15)', borderRadius: '8px', padding: '0.75rem', marginTop: '0.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'hsl(var(--accent-primary))', fontWeight: 500, fontSize: '0.8rem', marginBottom: '0.5rem' }}>
                  <Lock size={14} />
                  Import Session cho {platforms.find(p => p.id === activeSettingsPlatformId)?.name}
                </div>
                
                {connectError && <div style={{ color: 'hsl(var(--accent-error))', fontSize: '0.75rem', marginBottom: '4px' }}>{connectError}</div>}
                {connectSuccess && <div style={{ color: '#4ade80', fontSize: '0.75rem', marginBottom: '4px' }}>{connectSuccess}</div>}
                <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', lineHeight: 1.5, marginBottom: '0.5rem' }}>
                  Chạy Playwright local để login StackShare một lần, lưu file <code>stackshare_storage_state.json</code>, rồi upload file này vào đây. Docker chỉ dùng file đã import để Submit.
                </div>

                <div style={{ marginBottom: '0.5rem' }}>
                  <input
                    type="file"
                    accept="application/json,.json"
                    onChange={(e) => setSessionFile(e.target.files?.[0] || null)}
                    style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}
                  />
                  {sessionFile && (
                    <div style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))', marginTop: '4px' }}>
                      Đã chọn: {sessionFile.name}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                  <button
                    type="button"
                    onClick={() => setActiveSettingsPlatformId(null)}
                    style={{ background: 'none', border: 'none', color: 'hsl(var(--text-muted))', fontSize: '0.75rem', cursor: 'pointer', padding: '4px 8px' }}
                  >
                    Hủy
                  </button>
                  <button
                    type="button"
                    disabled={isConnectingPlatform}
                    onClick={() => handleImportPlatformSession(activeSettingsPlatformId)}
                    className="btn btn-primary"
                    style={{ padding: '4px 10px', fontSize: '0.75rem', width: 'auto' }}
                  >
                    {isConnectingPlatform ? 'Đang import...' : 'Import Session'}
                  </button>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmittingJob}
              className="btn btn-primary"
              style={{ marginTop: '0.25rem' }}
            >
              {isSubmittingJob ? (
                <div className="spinner"></div>
              ) : (
                <>
                  <Send size={16} /> Submit Website
                </>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* RIGHT PANEL: Live progress and submission history */}
      <div className="dashboard-panel scrollable-panel" style={{ minHeight: '550px' }}>
        
        {/* Anti-spam confirmation dialog */}
        {showConfirmDialog && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
            <div style={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '16px', padding: '1.5rem', maxWidth: '400px', textAlign: 'center', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)' }}>
              <ShieldCheck size={48} style={{ color: 'hsl(var(--accent-primary))', margin: '0 auto 1rem' }} />
              <h3 style={{ fontSize: '1.15rem', color: '#fff', marginBottom: '0.5rem' }}>Xác nhận yêu cầu Submit</h3>
              <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                Hành động này sẽ gửi yêu cầu submit URL website của bạn tới các SEO platform. Hãy chắc chắn thông tin URL và cấu hình xác thực đã chính xác.
              </p>
              <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
                <button
                  onClick={() => setShowConfirmDialog(false)}
                  className="btn btn-outline"
                  style={{ width: 'auto', padding: '0.5rem 1.25rem' }}
                >
                  Hủy bỏ
                </button>
                <button
                  onClick={executeSubmitJob}
                  className="btn btn-primary"
                  style={{ width: 'auto', padding: '0.5rem 1.25rem' }}
                >
                  Xác nhận
                </button>
              </div>
            </div>
          </div>
        )}

        {selectedJobId ? (
          /* JOB DETAILS & PROGRESS VIEW */
          <div>
            <div className="detail-header">
              <button 
                onClick={() => setSelectedJobId(null)}
                className="btn btn-outline"
                style={{ width: 'auto', padding: '0.5rem 1rem', display: 'inline-flex', marginBottom: '1.25rem' }}
              >
                <ArrowLeft size={16} /> Quay lại danh sách
              </button>

              {isLoadingJobDetails ? (
                <div className="loading-screen" style={{ minHeight: '200px' }}>
                  <div className="loading-dots"><div className="dot"></div><div className="dot"></div><div className="dot"></div></div>
                  <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem' }}>Đang tải tiến độ submit...</p>
                </div>
              ) : jobDetailsError ? (
                <div className="alert alert-error">
                  <AlertCircle size={18} />
                  <span>{jobDetailsError}</span>
                </div>
              ) : jobDetails ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <div>
                      <h2 className="detail-title" style={{ fontSize: '1.2rem', marginBottom: '4px' }}>Tiến độ submit website</h2>
                      <a 
                        href={jobDetails.websiteUrl} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        style={{ color: 'hsl(var(--accent-primary))', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}
                      >
                        {jobDetails.websiteUrl}
                        <ExternalLink size={12} />
                      </a>
                    </div>
                    <div className={`status-badge ${getStatusClass(jobDetails.status)}`}>
                      {getStatusLabel(jobDetails.status)}
                    </div>
                  </div>

                  <div className="audit-item-meta" style={{ marginTop: '0.85rem', marginBottom: '1.5rem', fontSize: '0.75rem' }}>
                    <div>Bắt đầu: {new Date(jobDetails.createdAt).toLocaleString('vi-VN')}</div>
                    {jobDetails.completedAt && <div>Hoàn thành: {new Date(jobDetails.completedAt).toLocaleString('vi-VN')}</div>}
                  </div>

                  {/* Platforms Status list */}
                  <h3 style={{ fontSize: '0.9rem', color: '#fff', fontWeight: 600, borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '0.5rem', marginBottom: '1rem', display: 'flex', gap: '6px', alignItems: 'center' }}>
                    <FileText size={16} /> Danh sách Platform ({jobDetails.details?.length || 0})
                  </h3>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {jobDetails.details.map(detail => {
                      const isExpanded = expandedDetailId === detail.detailId;
                      return (
                        <div 
                          key={detail.detailId} 
                          style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '8px', overflow: 'hidden' }}
                        >
                          {/* Row Header */}
                          <div 
                            onClick={() => setExpandedDetailId(isExpanded ? null : detail.detailId)}
                            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem', cursor: 'pointer', userSelect: 'none' }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              {detail.status === 'Success' ? (
                                <CheckCircle2 size={16} style={{ color: '#4ade80' }} />
                              ) : detail.status === 'Failed' ? (
                                <AlertCircle size={16} style={{ color: 'hsl(var(--accent-error))' }} />
                              ) : (
                                <div className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></div>
                              )}
                              <span style={{ fontSize: '0.85rem', fontWeight: 500, color: '#fff' }}>{detail.platformName}</span>
                              <span style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))' }}>({detail.platformCode.toUpperCase()})</span>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span className={`status-badge ${getStatusClass(detail.status)}`} style={{ fontSize: '0.7rem', padding: '2px 6px' }}>
                                {getStatusLabel(detail.status)}
                              </span>
                              {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                            </div>
                          </div>

                          {/* Collapsible content (Audit Logs & Details) */}
                          {isExpanded && (
                            <div style={{ padding: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.06)', background: 'rgba(0,0,0,0.15)', fontSize: '0.8rem' }}>
                              
                              {/* Error message if failed */}
                              {detail.errorMessage && (
                                <div className="alert alert-error" style={{ padding: '0.5rem 0.75rem', fontSize: '0.75rem', marginBottom: '0.75rem', borderRadius: '6px' }}>
                                  <AlertCircle size={14} />
                                  <span>{detail.errorMessage}</span>
                                </div>
                              )}

                              {/* Audit logs */}
                              <div style={{ marginBottom: '0.5rem' }}>
                                <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', fontWeight: 600, marginBottom: '0.25rem' }}>LOG HOẠT ĐỘNG:</div>
                                {detail.auditLogs?.length === 0 ? (
                                  <div style={{ color: 'hsl(var(--text-muted))', fontStyle: 'italic', fontSize: '0.75rem' }}>Không có nhật ký nào được ghi nhận.</div>
                                ) : (
                                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontFamily: 'monospace', fontSize: '0.72rem', background: '#0f172a', padding: '0.5rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.03)', maxHeight: '180px', overflowY: 'auto' }}>
                                    {detail.auditLogs.map(log => (
                                      <div key={log.id} style={{ display: 'flex', flexDirection: 'column', padding: '2px 0', borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', color: log.status === 'Failed' ? 'hsl(var(--accent-error))' : log.status === 'Success' ? '#4ade80' : 'hsl(var(--accent-primary))' }}>
                                          <span>[{new Date(log.timestamp).toLocaleTimeString()}] {log.action} ({log.status})</span>
                                          {log.durationMs && <span>{log.durationMs}ms</span>}
                                        </div>
                                        {log.logContent && <div style={{ color: 'hsl(var(--text-secondary))', paddingLeft: '8px', marginTop: '2px', whiteSpace: 'pre-wrap' }}>{log.logContent}</div>}
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        ) : (
          /* JOBS HISTORY LIST VIEW */
          <div>
            <div className="audit-list-header">
              <h2 className="audit-list-title">Lịch Sử Gửi Chỉ Mục</h2>
              <button 
                onClick={() => fetchJobs(true)} 
                disabled={isRefreshingHistory}
                className="refresh-btn"
                title="Tải lại danh sách"
              >
                <RefreshCw size={16} className={isRefreshingHistory ? 'spinner' : ''} />
              </button>
            </div>

            {isLoadingJobs ? (
              <div className="loading-screen" style={{ minHeight: '300px' }}>
                <div className="loading-dots"><div className="dot"></div><div className="dot"></div><div className="dot"></div></div>
                <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem' }}>Đang tải lịch sử submit...</p>
              </div>
            ) : jobsError ? (
              <div className="alert alert-error">
                <AlertCircle size={18} />
                <span>{jobsError}</span>
              </div>
            ) : jobs.length === 0 ? (
              <div className="detail-placeholder">
                <Globe size={48} style={{ color: 'hsl(var(--text-muted))' }} />
                <h3>Chưa có lịch sử submit</h3>
                <p style={{ fontSize: '0.85rem', maxWidth: '350px' }}>Nhập URL website ở biểu mẫu bên trái, cấu hình platforms và nhấn Submit để khai báo chỉ mục cho website của bạn.</p>
              </div>
            ) : (
              <div className="audit-items-container">
                {jobs.map((job) => (
                  <div 
                    key={job.jobId} 
                    onClick={() => setSelectedJobId(job.jobId)}
                    className="audit-item-card"
                  >
                    <div className="audit-item-info">
                      <div className="audit-item-url">{job.websiteUrl}</div>
                      <div className="audit-item-meta" style={{ fontSize: '0.7rem' }}>
                        <span style={{ color: '#fff', fontWeight: 500 }}>
                          Platforms: {job.details?.map(d => d.platformName).join(', ') || 'N/A'}
                        </span>
                        <span>•</span>
                        <span>{new Date(job.createdAt).toLocaleString('vi-VN')}</span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span className={`status-badge ${getStatusClass(job.status)}`} style={{ fontSize: '0.72rem', padding: '3px 8px' }}>
                        {getStatusLabel(job.status)}
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
