import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LogOut, Globe, Mail, ShieldCheck, AlertCircle, 
  CheckCircle2, RefreshCw, ArrowLeft, ArrowRight, ExternalLink, 
  Lock, ChevronDown, ChevronUp, FileText, Settings, Send,
  Layers, Copy, Check, Terminal, FileJson, Info, Eye, Search, Filter
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
  const [submitterName, setSubmitterName] = useState('');
  const [futureToolsCategory, setFutureToolsCategory] = useState('Productivity');
  const [futureToolsPricing, setFutureToolsPricing] = useState('Free');
  const [futureToolsNewsletterOptIn, setFutureToolsNewsletterOptIn] = useState(false);
  
  // Dashboard platform selection & filtering
  const [platforms, setPlatforms] = useState([]);
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(true);
  const [selectedPlatformId, setSelectedPlatformId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [methodFilter, setMethodFilter] = useState('ALL'); // 'ALL', 'API', 'AUTOMATION'
  
  // Platform settings
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
  const [copiedDataId, setCopiedDataId] = useState(null);

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
      
      const preferredCodes = ['futuretools', 'productburst', 'stackshare'];
      const preferredPlatform = preferredCodes
        .map((code) => data.find((platform) => platform.code?.toLowerCase() === code))
        .find(Boolean);

      // Auto-select the preferred platform by default
      if (preferredPlatform) {
        setSelectedPlatformId(preferredPlatform.id);
      } else if (data.length > 0) {
        setSelectedPlatformId(data[0].id);
      }
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
    if (!selectedPlatformId) return setSubmitError('Vui lòng chọn một platform.');

    try {
      new URL(url);
    } catch (_) {
      return setSubmitError('Định dạng URL không hợp lệ (ví dụ: https://example.com).');
    }

    const currentPlatform = platforms.find(p => p.id === selectedPlatformId);
    const isASR = currentPlatform?.code?.toLowerCase() === 'asr' || currentPlatform?.code?.toLowerCase() === 'active_search_results';
    const isFutureTools = currentPlatform?.code?.toLowerCase() === 'futuretools';
    
    if (isASR && !contactEmail) {
      return setSubmitError('Vui lòng nhập Contact Email cho Active Search Results.');
    }

    if (isFutureTools) {
      if (!submitterName) return setSubmitError('Vui lòng nhập Your Name cho Future Tools.');
      if (!siteName) return setSubmitError('Vui lòng nhập Tool Name cho Future Tools.');
      if (!description) return setSubmitError('Vui lòng nhập Short Description cho Future Tools.');
      if (!contactEmail) return setSubmitError('Vui lòng nhập Your Email cho Future Tools.');
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
          platformIds: [selectedPlatformId],
          siteName: siteName || undefined,
          description: description || undefined,
          sitemapUrl: sitemapUrl || undefined,
          contactEmail: contactEmail || undefined,
          yourName: submitterName || undefined,
          category: futureToolsCategory || undefined,
          pricing: futureToolsPricing || undefined,
          newsletterOptIn: futureToolsNewsletterOptIn ? 'true' : undefined
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.Message || 'Gửi yêu cầu submit thất bại.');
      }
      
      const data = await response.json();
      setSubmitSuccess('Gửi yêu cầu thành công! Đang tiến hành submit bất đồng bộ...');
      
      // Reset form URL, keep contactEmail for convenience
      setUrl('');
      
      fetchJobs(true);
      if (data.jobId) { 
        setSelectedJobId(data.jobId);
      }
    } catch (err) {
      setSubmitError(err.message);
    } finally {
      setIsSubmittingJob(false);
    }
  };

  // Initial Load
  useEffect(() => {
    fetchPlatforms();
    fetchJobs();
  }, []);

  useEffect(() => {
    const fallbackName = currentUser?.displayName || currentUser?.email?.split('@')?.[0] || '';
    if (!submitterName && fallbackName) {
      setSubmitterName(fallbackName);
    }
  }, [currentUser, submitterName]);

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

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedDataId(id);
    setTimeout(() => setCopiedDataId(null), 2000);
  };

  // Filtered platforms logic
  const filteredPlatforms = platforms.filter(platform => {
    const matchesSearch = platform.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          platform.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMethod = methodFilter === 'ALL' ||
                          (methodFilter === 'API' && platform.submitMethod === 'API') ||
                          (methodFilter === 'AUTOMATION' && platform.submitMethod !== 'API');
    return matchesSearch && matchesMethod;
  });

  const activePlatform = platforms.find(p => p.id === selectedPlatformId);
  const isActivePlatformStackShare = activePlatform?.code?.toLowerCase() === 'stackshare';
  const isActivePlatformASR = activePlatform?.code?.toLowerCase() === 'asr' || activePlatform?.code?.toLowerCase() === 'active_search_results';
  const isActivePlatformFutureTools = activePlatform?.code?.toLowerCase() === 'futuretools';

  // Platform specific static metadata for visual cards (like tags and short descriptions in the reference image)
  const getPlatformMetadata = (code) => {
    const normalized = code?.toLowerCase();
    if (normalized === 'stackshare') {
      return {
        tags: ['Developer Tools', 'Automation', 'Social'],
        description: 'Tự động mở trình duyệt chạy ngầm để điền form, crawl dữ liệu website và submit công cụ lập trình của bạn.',
        speed: '2-3 phút',
        cost: 'Free',
        typeLabel: 'AUTOMATION'
      };
    }
    if (normalized === 'futuretools') {
      return {
        tags: ['AI Tools', 'No Login', 'Automation'],
        description: 'Mở trang submit của Future Tools, tự động điền form giới thiệu công cụ AI và bấm submit bằng browser thật.',
        speed: '1-2 phút',
        cost: 'Free',
        typeLabel: 'AUTOMATION'
      };
    }
    if (normalized === 'asr' || normalized === 'active_search_results') {
      return {
        tags: ['SEO Directory', 'HTTP Direct', 'Instant'],
        description: 'Gửi HTTP POST request trực tiếp lên danh bạ Active Search Results để index website nhanh chóng và miễn phí.',
        speed: 'Tức thì',
        cost: 'Free',
        typeLabel: 'API DIRECT'
      };
    }
    return {
      tags: ['SEO Platform', 'Indexing'],
      description: 'Nền tảng hỗ trợ Submit website giúp tối ưu chỉ mục công cụ tìm kiếm và danh bạ internet.',
      speed: 'Tùy biến',
      cost: 'Free',
      typeLabel: 'SUBMIT'
    };
  };

  return (
    <div className="dashboard-grid">
      {/* LEFT COLUMN: Profile, Navigation & Indexing History */}
      <div className="dashboard-panel">
        {/* Profile Card */}
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
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
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

        {/* JOBS HISTORY LIST VIEW */}
        <div>
          <div className="audit-list-header">
            <h2 className="audit-list-title" style={{ fontSize: '1.05rem', fontWeight: 600 }}>Lịch Sử Gửi Chỉ Mục</h2>
            <button 
              onClick={() => fetchJobs(true)} 
              disabled={isRefreshingHistory}
              className="refresh-btn"
              title="Tải lại danh sách"
            >
              <RefreshCw size={14} className={isRefreshingHistory ? 'spinner' : ''} />
            </button>
          </div>

          {isLoadingJobs ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem 0' }}>
              <div className="spinner" style={{ width: '20px', height: '20px' }}></div>
            </div>
          ) : jobsError ? (
            <div className="alert alert-error" style={{ fontSize: '0.75rem', padding: '0.5rem' }}>
              <AlertCircle size={14} />
              <span>{jobsError}</span>
            </div>
          ) : jobs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '1.5rem', color: 'hsl(var(--text-muted))', fontSize: '0.78rem', border: '1px dashed var(--border-glass)', borderRadius: '12px' }}>
              Chưa có lịch sử submit.
            </div>
          ) : (
            <div className="audit-items-container" style={{ maxHeight: '450px', overflowY: 'auto', gap: '0.5rem' }}>
              {jobs.map((job) => {
                const isActiveJob = selectedJobId === job.jobId;
                return (
                  <div 
                    key={job.jobId} 
                    onClick={() => {
                      setSelectedJobId(job.jobId);
                      setSubmitError('');
                      setSubmitSuccess('');
                    }}
                    className={`audit-item-card ${isActiveJob ? 'active' : ''}`}
                    style={{ padding: '0.85rem', cursor: 'pointer', margin: 0 }}
                  >
                    <div className="audit-item-info">
                      <div className="audit-item-url" style={{ fontSize: '0.85rem' }}>{job.websiteUrl}</div>
                      <div className="audit-item-meta" style={{ fontSize: '0.68rem', gap: '4px' }}>
                        <span style={{ color: 'hsl(var(--text-secondary))' }}>
                          {job.details?.map(d => d.platformName).join(', ') || 'N/A'}
                        </span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span className={`status-badge ${getStatusClass(job.status)}`} style={{ fontSize: '0.62rem', padding: '1px 4px' }}>
                        {job.status === 'Completed' || job.status === 'Success' ? 'Xong' : getStatusLabel(job.status)}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT COLUMN (Wider Panel): Dynamic workspace - Platform grid & submit form, OR Job Details page */}
      <div className="dashboard-panel scrollable-panel" style={{ minHeight: '550px' }}>
        
        {/* Anti-spam confirmation dialog */}
        {showConfirmDialog && (
          <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
            <div style={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '16px', padding: '1.5rem', maxWidth: '400px', textAlign: 'center', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)' }}>
              <ShieldCheck size={48} style={{ color: 'hsl(var(--accent-primary))', margin: '0 auto 1rem' }} />
              <h3 style={{ fontSize: '1.15rem', color: '#fff', marginBottom: '0.5rem' }}>Xác nhận Submit</h3>
              <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                Gửi yêu cầu submit URL website tới platform <strong>{activePlatform?.name}</strong>.
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
          /* ==========================================
             VIEW 1: DETAILED PROGRESS / CRAWL DETAILS 
             ========================================== */
          <div>
            <div className="detail-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '1rem' }}>
              <button 
                onClick={() => setSelectedJobId(null)}
                className="btn btn-outline"
                style={{ width: 'auto', padding: '0.4rem 0.85rem', fontSize: '0.8rem', display: 'inline-flex', gap: '4px', margin: 0 }}
              >
                <ArrowLeft size={14} /> Trở lại danh mục
              </button>

              {jobDetails && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div className={`status-badge ${getStatusClass(jobDetails.status)}`} style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
                    {getStatusLabel(jobDetails.status)}
                  </div>
                </div>
              )}
            </div>

            {isLoadingJobDetails ? (
              <div className="loading-screen" style={{ minHeight: '300px' }}>
                <div className="loading-dots"><div className="dot"></div><div className="dot"></div><div className="dot"></div></div>
                <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem' }}>Đang tải tiến trình...</p>
              </div>
            ) : jobDetailsError ? (
              <div className="alert alert-error" style={{ marginTop: '1.5rem' }}>
                <AlertCircle size={18} />
                <span>{jobDetailsError}</span>
              </div>
            ) : jobDetails ? (
              <div style={{ marginTop: '1.25rem' }}>
                {/* Website overview card */}
                <div style={{ background: 'rgba(255,255,255,0.01)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '16px', padding: '1.25rem', marginBottom: '1.5rem' }}>
                  <span style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    Website Submit
                  </span>
                  <h2 style={{ fontSize: '1.3rem', color: '#fff', fontWeight: 700, marginTop: '4px', wordBreak: 'break-all', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Globe size={20} style={{ color: 'hsl(var(--accent-primary))' }} />
                    <a href={jobDetails.websiteUrl} target="_blank" rel="noopener noreferrer" style={{ color: '#fff', textDecoration: 'none' }}>
                      {jobDetails.websiteUrl}
                    </a>
                    <ExternalLink size={14} style={{ color: 'hsl(var(--text-muted))' }} />
                  </h2>
                  <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-secondary))', marginTop: '6px' }}>
                    Tạo lúc: {new Date(jobDetails.createdAt).toLocaleString('vi-VN')}
                  </div>
                </div>

                <h3 style={{ fontSize: '0.95rem', color: '#fff', fontWeight: 600, marginBottom: '0.85rem', display: 'flex', gap: '6px', alignItems: 'center' }}>
                  <FileText size={16} /> Chi tiết platforms ({jobDetails.details?.length || 0})
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  {jobDetails.details.map(detail => {
                    const isExpanded = expandedDetailId === detail.detailId;
                    const isDetailStackShare = detail.platformCode?.toLowerCase() === 'stackshare';

                    // Parse crawled data
                    let crawledData = null;
                    if (detail.responseData) {
                      try {
                        const parsed = JSON.parse(detail.responseData);
                        if (parsed && parsed.crawled_data) {
                          crawledData = parsed.crawled_data;
                        }
                      } catch (e) {
                        // ResponseData isn't JSON
                      }
                    }

                    return (
                      <div 
                        key={detail.detailId} 
                        style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '12px', overflow: 'hidden' }}
                      >
                        {/* Detail Platform Row Header */}
                        <div 
                          onClick={() => setExpandedDetailId(isExpanded ? null : detail.detailId)}
                          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.85rem 1.25rem', cursor: 'pointer', userSelect: 'none' }}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                            {detail.status === 'Success' || detail.status === 'Completed' ? (
                              <CheckCircle2 size={18} style={{ color: '#4ade80' }} />
                            ) : detail.status === 'Failed' ? (
                              <AlertCircle size={18} style={{ color: 'hsl(var(--accent-error))' }} />
                            ) : (
                              <div className="spinner" style={{ width: '15px', height: '15px', borderWidth: '2px' }}></div>
                            )}
                            <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#fff' }}>{detail.platformName}</span>
                            <span style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))' }}>({detail.platformCode.toUpperCase()})</span>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span className={`status-badge ${getStatusClass(detail.status)}`} style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                              {getStatusLabel(detail.status)}
                            </span>
                            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </div>
                        </div>

                        {/* Detail Collapsible Container */}
                        {isExpanded && (
                          <div style={{ padding: '1.25rem', borderTop: '1px solid rgba(255,255,255,0.06)', background: 'rgba(0,0,0,0.18)', fontSize: '0.8rem' }}>
                            
                            {detail.errorMessage && (
                              <div className="alert alert-error" style={{ padding: '0.6rem 0.85rem', fontSize: '0.75rem', marginBottom: '0.85rem', borderRadius: '6px' }}>
                                <AlertCircle size={14} />
                                <span>{detail.errorMessage}</span>
                              </div>
                            )}

                            {/* CRAWLED DATA PREVIEW FOR STACKSHARE */}
                            {isDetailStackShare && crawledData && (
                              <div style={{ marginBottom: '1.25rem', padding: '1rem', background: 'rgba(74, 222, 128, 0.04)', border: '1px solid rgba(74, 222, 128, 0.18)', borderRadius: '10px' }}>
                                <h4 style={{ fontSize: '0.85rem', color: '#4ade80', fontWeight: 600, marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                  <CheckCircle2 size={15} /> Dữ liệu crawl trích xuất thành công:
                                </h4>
                                
                                <div style={{ display: 'grid', gridTemplateColumns: crawledData.logo ? '60px 1fr' : '1fr', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
                                  {crawledData.logo && (
                                    <img 
                                      src={crawledData.logo} 
                                      alt="Logo" 
                                      style={{ width: '60px', height: '60px', borderRadius: '10px', background: '#fff', objectFit: 'contain', padding: '4px', border: '1px solid rgba(255,255,255,0.1)' }}
                                      onError={(e) => e.currentTarget.style.display = 'none'}
                                    />
                                  )}
                                  <div>
                                    <div style={{ fontSize: '1rem', fontWeight: 700, color: '#fff' }}>
                                      {crawledData.tool_name || 'N/A'}
                                    </div>
                                    {crawledData.website_url && (
                                      <a href={crawledData.website_url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.75rem', color: 'hsl(var(--accent-primary))', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                                        {crawledData.website_url} <ExternalLink size={10} />
                                      </a>
                                    )}
                                  </div>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.8rem', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '0.75rem' }}>
                                  {crawledData.short_description && (
                                    <div>
                                      <span style={{ color: 'hsl(var(--text-secondary))', fontWeight: 600 }}>Mô tả ngắn:</span>{' '}
                                      <span style={{ color: 'hsl(var(--text-primary))' }}>{crawledData.short_description}</span>
                                    </div>
                                  )}
                                  {crawledData.description && (
                                    <div>
                                      <span style={{ color: 'hsl(var(--text-secondary))', fontWeight: 600 }}>Mô tả chi tiết:</span>{' '}
                                      <span style={{ color: 'hsl(var(--text-primary))' }}>{crawledData.description}</span>
                                    </div>
                                  )}
                                  {crawledData.features && (
                                    <div>
                                      <span style={{ color: 'hsl(var(--text-secondary))', fontWeight: 600 }}>Tính năng / Tag:</span>{' '}
                                      <span style={{ color: 'hsl(var(--text-primary))' }}>{crawledData.features}</span>
                                    </div>
                                  )}
                                  {crawledData.docs_url && (
                                    <div>
                                      <span style={{ color: 'hsl(var(--text-secondary))', fontWeight: 600 }}>Tài liệu (Docs):</span>{' '}
                                      <a href={crawledData.docs_url} target="_blank" rel="noopener noreferrer" style={{ color: 'hsl(var(--accent-primary))', textDecoration: 'none' }}>
                                        {crawledData.docs_url}
                                      </a>
                                    </div>
                                  )}
                                </div>

                                {/* Actions */}
                                <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      const pre = e.currentTarget.parentNode.nextElementSibling;
                                      pre.style.display = pre.style.display === 'none' ? 'block' : 'none';
                                    }}
                                    className="btn btn-outline"
                                    style={{ width: 'auto', padding: '4px 10px', fontSize: '0.7rem', display: 'inline-flex', gap: '4px', margin: 0 }}
                                  >
                                    <FileJson size={12} /> Xem JSON raw
                                  </button>
                                  <button
                                    type="button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      copyToClipboard(JSON.stringify(crawledData, null, 2), detail.detailId);
                                    }}
                                    className="btn btn-outline"
                                    style={{ width: 'auto', padding: '4px 10px', fontSize: '0.7rem', display: 'inline-flex', gap: '4px', margin: 0 }}
                                  >
                                    {copiedDataId === detail.detailId ? <Check size={12} style={{ color: '#4ade80' }} /> : <Copy size={12} />}
                                    {copiedDataId === detail.detailId ? 'Đã copy!' : 'Copy JSON'}
                                  </button>
                                </div>
                                <pre style={{ display: 'none', marginTop: '0.65rem', padding: '0.65rem', background: '#090d16', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '6px', fontSize: '0.72rem', color: '#94a3b8', overflowX: 'auto', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                                  {JSON.stringify(crawledData, null, 2)}
                                </pre>
                              </div>
                            )}

                            {/* ASR direct HTTP logs */}
                            {!isDetailStackShare && detail.responseData && (
                              <div style={{ marginBottom: '1.25rem', padding: '0.85rem', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '8px' }}>
                                <span style={{ color: 'hsl(var(--text-secondary))', fontWeight: 600, fontSize: '0.75rem' }}>Phản hồi HTTP:</span>
                                <div style={{ color: 'hsl(var(--text-primary))', fontSize: '0.75rem', fontFamily: 'monospace', marginTop: '4px', wordBreak: 'break-all' }}>
                                  {detail.responseData}
                                </div>
                              </div>
                            )}

                            {/* Audit Logs Console */}
                            <div>
                              <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', fontWeight: 600, marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <Terminal size={12} /> NHẬT KÝ HOẠT ĐỘNG:
                              </div>
                              {detail.auditLogs?.length === 0 ? (
                                <div style={{ color: 'hsl(var(--text-muted))', fontStyle: 'italic', fontSize: '0.72rem' }}>Không có nhật ký.</div>
                              ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontFamily: 'monospace', fontSize: '0.72rem', background: '#0f172a', padding: '0.65rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.03)', maxHeight: '180px', overflowY: 'auto' }}>
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
        ) : (
          /* ==========================================
             VIEW 2: DYNAMIC PLATFORM CATALOG & SUBMIT FORM
             ========================================== */
          <div>
            {/* Catalog Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff', background: 'linear-gradient(135deg, #fff 40%, hsl(var(--text-secondary)) 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-0.5px' }}>
                  SEO Platforms Directory
                </h1>
                <p style={{ color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', marginTop: '2px' }}>
                  Chọn một platform bên dưới để tự động submit và khai báo chỉ mục cho website.
                </p>
              </div>
            </div>

            {/* Catalog Filters Bar (Uplizd style) */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '12px', padding: '0.75rem 1rem', marginBottom: '1.5rem' }}>
              
              {/* Method filter toggle */}
              <div style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.25)', padding: '3px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)' }}>
                <button
                  type="button"
                  onClick={() => setMethodFilter('ALL')}
                  style={{
                    background: methodFilter === 'ALL' ? 'rgba(255,255,255,0.08)' : 'none',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '0.75rem',
                    color: methodFilter === 'ALL' ? '#fff' : 'hsl(var(--text-secondary))',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  Tất cả
                </button>
                <button
                  type="button"
                  onClick={() => setMethodFilter('API')}
                  style={{
                    background: methodFilter === 'API' ? 'rgba(255,255,255,0.08)' : 'none',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '0.75rem',
                    color: methodFilter === 'API' ? '#fff' : 'hsl(var(--text-secondary))',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  Direct API
                </button>
                <button
                  type="button"
                  onClick={() => setMethodFilter('AUTOMATION')}
                  style={{
                    background: methodFilter === 'AUTOMATION' ? 'rgba(255,255,255,0.08)' : 'none',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '4px 10px',
                    fontSize: '0.75rem',
                    color: methodFilter === 'AUTOMATION' ? '#fff' : 'hsl(var(--text-secondary))',
                    cursor: 'pointer',
                    fontWeight: 500
                  }}
                >
                  UI Automation
                </button>
              </div>

              {/* Search bar */}
              <div style={{ position: 'relative', width: '220px' }}>
                <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'hsl(var(--text-muted))' }} />
                <input
                  type="text"
                  placeholder="Tìm platform..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '6px 10px 6px 30px',
                    borderRadius: '8px',
                    background: 'rgba(0, 0, 0, 0.25)',
                    border: '1px solid var(--border-glass)',
                    color: '#fff',
                    fontSize: '0.8rem',
                    outline: 'none'
                  }}
                />
              </div>
            </div>

            {/* Platform Grid (Uplizd style) */}
            {isLoadingPlatforms ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem 0' }}>
                <div className="spinner" style={{ width: '30px', height: '30px', borderWidth: '3.5px' }}></div>
              </div>
            ) : filteredPlatforms.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem 1.5rem', color: 'hsl(var(--text-secondary))', border: '1px dashed rgba(255,255,255,0.06)', borderRadius: '16px' }}>
                Không tìm thấy platform nào khớp với từ khóa tìm kiếm hoặc bộ lọc.
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
                {filteredPlatforms.map(platform => {
                  const isSelected = selectedPlatformId === platform.id;
                  const isSS = platform.code?.toLowerCase() === 'stackshare';
                  const meta = getPlatformMetadata(platform.code);
                  
                  return (
                    <div
                      key={platform.id}
                      onClick={() => {
                        setSelectedPlatformId(platform.id);
                        setSubmitError('');
                        setSubmitSuccess('');
                      }}
                      style={{
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: isSelected ? '2px solid hsl(var(--accent-primary))' : '1px solid var(--border-glass)',
                        borderRadius: '20px',
                        padding: '1.25rem',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        minHeight: '200px',
                        cursor: 'pointer',
                        position: 'relative',
                        transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
                        boxShadow: isSelected ? '0 10px 25px -5px hsl(var(--accent-primary) / 0.15)' : 'none',
                        transform: isSelected ? 'translateY(-4px)' : 'none',
                      }}
                    >
                      {/* Top Type Label */}
                      <span style={{
                        position: 'absolute',
                        top: '12px',
                        right: '12px',
                        fontSize: '0.62rem',
                        background: isSelected ? 'hsl(var(--accent-primary) / 0.15)' : 'rgba(255, 255, 255, 0.04)',
                        border: isSelected ? '1px solid hsl(var(--accent-primary) / 0.3)' : '1px solid var(--border-glass)',
                        padding: '2px 8px',
                        borderRadius: '9999px',
                        color: isSelected ? 'hsl(var(--accent-primary))' : 'hsl(var(--text-secondary))',
                        fontWeight: 600,
                        letterSpacing: '0.5px'
                      }}>
                        {meta.typeLabel}
                      </span>

                      {/* Header (Icon + Title) */}
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '0.75rem', width: '80%' }}>
                          <div style={{
                            width: '36px',
                            height: '36px',
                            borderRadius: '10px',
                            background: isSelected ? 'hsl(var(--accent-primary) / 0.1)' : 'rgba(255,255,255,0.03)',
                            border: isSelected ? '1px solid hsl(var(--accent-primary) / 0.2)' : '1px solid var(--border-glass)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: isSelected ? 'hsl(var(--accent-primary))' : 'hsl(var(--text-secondary))'
                          }}>
                            {isSS ? <Layers size={18} /> : <Globe size={18} />}
                          </div>
                          <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {platform.name}
                          </span>
                        </div>

                        {/* Tags */}
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '0.75rem' }}>
                          {meta.tags.map(tag => (
                            <span key={tag} style={{
                              fontSize: '0.62rem',
                              background: 'rgba(255, 255, 255, 0.03)',
                              border: '1px solid rgba(255, 255, 255, 0.05)',
                              padding: '1px 6px',
                              borderRadius: '4px',
                              color: 'hsl(var(--text-secondary))'
                            }}>
                              {tag}
                            </span>
                          ))}
                        </div>

                        {/* Description */}
                        <p style={{
                          fontSize: '0.75rem',
                          color: 'hsl(var(--text-secondary))',
                          lineHeight: 1.4,
                          marginBottom: '1rem',
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          height: '3.2em'
                        }}>
                          {meta.description}
                        </p>
                      </div>

                      {/* Footer */}
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        borderTop: '1px solid rgba(255, 255, 255, 0.04)',
                        paddingTop: '0.75rem',
                        fontSize: '0.7rem',
                        color: 'hsl(var(--text-muted))'
                      }}>
                        <span>Tốc độ: {meta.speed}</span>
                        <span style={{
                          background: 'rgba(34, 197, 94, 0.08)',
                          border: '1px solid rgba(34, 197, 94, 0.15)',
                          color: '#4ade80',
                          padding: '1px 6px',
                          borderRadius: '4px',
                          fontWeight: 600
                        }}>
                          {meta.cost}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Submit Form Area (renders under catalog for the active selection) */}
            {activePlatform && (
              <div className="auth-container" style={{
                maxWidth: '100%',
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '2rem',
                border: '1px solid rgba(255, 255, 255, 0.06)',
                borderRadius: '24px',
                marginTop: '2rem',
                animation: 'none'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
                  <h2 className="form-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
                    {isActivePlatformStackShare ? <Layers size={20} className="input-icon-static" style={{ color: 'hsl(var(--accent-primary))' }} /> : <Globe size={20} className="input-icon-static" style={{ color: 'hsl(var(--accent-primary))' }} />}
                    {isActivePlatformFutureTools ? 'Submit Tool to Future Tools' : `Submit Website to ${activePlatform.name}`}
                  </h2>
                </div>

                {isActivePlatformFutureTools && (
                  <div style={{ marginBottom: '0.25rem', color: 'hsl(var(--text-secondary))', fontSize: '0.85rem', lineHeight: 1.5 }}>
                    Điền theo đúng form FutureTools: tên người submit, tên tool, URL, mô tả ngắn, category, pricing, email và checkbox newsletter.
                  </div>
                )}

                <form onSubmit={handleFormSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  {submitError && (
                    <div className="alert alert-error" style={{ padding: '0.65rem 0.85rem', marginBottom: 0 }}>
                      <AlertCircle size={16} />
                      <span style={{ fontSize: '0.8rem' }}>{submitError}</span>
                    </div>
                  )}
                  {submitSuccess && (
                    <div className="alert alert-success" style={{ padding: '0.65rem 0.85rem', marginBottom: 0 }}>
                      <CheckCircle2 size={16} />
                      <span style={{ fontSize: '0.8rem' }}>{submitSuccess}</span>
                    </div>
                  )}

                  {/* FORM FIELDS */}
                  {isActivePlatformFutureTools ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Your Name *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="Jane Doe"
                            value={submitterName}
                            onChange={(e) => setSubmitterName(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Tool Name *</label>
                        <div className="input-wrapper">
                          <FileText size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="e.g. ChatGPT"
                            value={siteName}
                            onChange={(e) => setSiteName(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Tool URL *</label>
                        <div className="input-wrapper">
                          <Globe size={18} className="input-icon" />
                          <input
                            type="text"
                            placeholder="https://your-tool.com"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Short Description *</label>
                        <div className="input-wrapper" style={{ alignItems: 'flex-start' }}>
                          <FileText size={18} className="input-icon" style={{ marginTop: '0.7rem' }} />
                          <textarea
                            placeholder="Briefly describe what the tool does..."
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            className="form-input"
                            rows={4}
                            required
                          />
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Category *</label>
                          <select
                            className="form-input"
                            value={futureToolsCategory}
                            onChange={(e) => setFutureToolsCategory(e.target.value)}
                          >
                            {['Chat', 'Generative Art', 'Generative Video', 'Generative Code', 'Text-To-Speech', 'Search Engines', 'Productivity', 'Marketing', 'Design', 'Writing', 'Music', 'Research', 'Education', 'Finance', 'Healthcare', 'Legal', 'Sales', 'Customer Support', 'Other'].map((option) => (
                              <option key={option} value={option}>{option}</option>
                            ))}
                          </select>
                        </div>

                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Pricing *</label>
                          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                            {['Free', 'Freemium', 'Paid', 'Open Source'].map((option) => {
                              const active = futureToolsPricing === option;
                              return (
                                <button
                                  key={option}
                                  type="button"
                                  onClick={() => setFutureToolsPricing(option)}
                                  className="btn btn-outline"
                                  style={{
                                    width: 'auto',
                                    padding: '0.45rem 0.75rem',
                                    borderColor: active ? 'hsl(var(--accent-primary))' : undefined,
                                    color: active ? '#fff' : undefined,
                                    background: active ? 'hsl(var(--accent-primary) / 0.12)' : undefined,
                                  }}
                                >
                                  {option}
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      </div>

                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Your Email *</label>
                        <div className="input-wrapper">
                          <Mail size={18} className="input-icon" />
                          <input
                            type="email"
                            placeholder="you@example.com"
                            value={contactEmail}
                            onChange={(e) => setContactEmail(e.target.value)}
                            className="form-input"
                            required
                          />
                        </div>
                      </div>

                      <label style={{ display: 'flex', alignItems: 'flex-start', gap: '0.6rem', cursor: 'pointer', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', padding: '0.85rem 1rem' }}>
                        <input
                          type="checkbox"
                          checked={futureToolsNewsletterOptIn}
                          onChange={(e) => setFutureToolsNewsletterOptIn(e.target.checked)}
                          style={{ marginTop: '0.15rem' }}
                        />
                        <span style={{ fontSize: '0.85rem', color: 'hsl(var(--text-secondary))' }}>
                          Join the Future Tools newsletter for AI news and tool recommendations. (Optional)
                        </span>
                      </label>
                    </div>
                  ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: isActivePlatformASR ? '1fr 1fr' : '1fr', gap: '1rem' }}>
                      <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Website URL cần submit *</label>
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

                      {isActivePlatformASR && (
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label className="form-label">Email liên hệ (Contact Email) *</label>
                          <div className="input-wrapper">
                            <Mail size={18} className="input-icon" />
                            <input
                              type="email"
                              placeholder="admin@example.com"
                              value={contactEmail}
                              onChange={(e) => setContactEmail(e.target.value)}
                              className="form-input"
                              required
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* StackShare Session import form inside the form wrapper */}
                  {isActivePlatformStackShare && (
                    <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.8rem', color: 'hsl(var(--text-secondary))', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Lock size={14} style={{ color: 'hsl(var(--accent-primary))' }} /> Cấu hình Automation Browser Session
                        </span>
                        <button
                          type="button"
                          onClick={() => {
                            setActiveSettingsPlatformId(
                              activeSettingsPlatformId === activePlatform.id ? null : activePlatform.id
                            );
                            setConnectSuccess('');
                            setConnectError('');
                          }}
                          className="refresh-btn"
                          style={{ padding: '2px', color: activeSettingsPlatformId ? 'hsl(var(--accent-primary))' : 'inherit' }}
                          title="Import Playwright Session JSON"
                        >
                          <Settings size={14} />
                        </button>
                      </div>

                      {activeSettingsPlatformId === activePlatform.id ? (
                        <div style={{ background: 'rgba(59, 130, 246, 0.05)', border: '1px solid rgba(59, 130, 246, 0.12)', borderRadius: '12px', padding: '1rem', marginBottom: '1rem' }}>
                          <div style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', lineHeight: 1.4, marginBottom: '0.65rem' }}>
                            Chạy Playwright local, lưu file <code>stackshare_storage_state.json</code>, rồi upload JSON đó vào đây để tự động hóa đăng nhập.
                          </div>
                          
                          {connectError && <div style={{ color: 'hsl(var(--accent-error))', fontSize: '0.75rem', marginBottom: '4px' }}>{connectError}</div>}
                          {connectSuccess && <div style={{ color: '#4ade80', fontSize: '0.75rem', marginBottom: '4px' }}>{connectSuccess}</div>}
                          
                          <div style={{ marginBottom: '0.75rem' }}>
                            <input
                              type="file"
                              accept="application/json,.json"
                              onChange={(e) => setSessionFile(e.target.files?.[0] || null)}
                              style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}
                            />
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
                              onClick={() => handleImportPlatformSession(activePlatform.id)}
                              className="btn btn-primary"
                              style={{ padding: '4px 12px', fontSize: '0.75rem', width: 'auto' }}
                            >
                              {isConnectingPlatform ? 'Đang import...' : 'Import'}
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div style={{ fontSize: '0.72rem', color: 'hsl(var(--text-muted))', fontStyle: 'italic' }}>
                          * Platform này sử dụng Chromium UI Automation chạy ngầm để điền form tự động.
                        </div>
                      )}
                    </div>
                  )}

                  {/* Submit buttons */}
                  <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '1rem' }}>
                    <button
                      type="submit"
                      disabled={isSubmittingJob}
                      className="btn btn-primary"
                      style={{ width: 'auto', padding: '0.75rem 2rem', fontSize: '0.9rem' }}
                    >
                          {isSubmittingJob ? (
                            <div className="spinner"></div>
                          ) : (
                            <>
                              <Send size={16} /> 
                          {isActivePlatformFutureTools ? 'Submit Tool' : (isActivePlatformStackShare ? 'Crawl & Submit Website' : 'Submit Website Direct')}
                            </>
                          )}
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
