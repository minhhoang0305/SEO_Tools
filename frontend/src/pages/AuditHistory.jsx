import { useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Calendar,
  CheckCircle2,
  ExternalLink,
  FileText,
  History,
  Info,
  Plus,
  RefreshCw,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5001';

const statusMap = {
  0: ['Đang chờ', 'pending'],
  1: ['Đang phân tích', 'processing'],
  2: ['Đã hoàn thành', 'completed'],
  3: ['Thất bại', 'failed'],
  Pending: ['Đang chờ', 'pending'],
  Processing: ['Đang phân tích', 'processing'],
  Completed: ['Đã hoàn thành', 'completed'],
  Failed: ['Thất bại', 'failed'],
};

function getStatus(status) {
  return statusMap[status] ?? [String(status ?? 'Thất bại'), 'failed'];
}

function ScoreRing({ value = 0, label, tone }) {
  const score = Math.min(100, Math.max(0, Number(value) || 0));
  const circumference = 2 * Math.PI * 38;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className={`metric-card ${tone}`}>
      <svg className="score-ring" viewBox="0 0 96 96" role="img" aria-label={`${label}: ${score}`}>
        <circle cx="48" cy="48" r="38" className="score-ring-track" />
        <circle cx="48" cy="48" r="38" className="score-ring-value" strokeDasharray={circumference} strokeDashoffset={offset} />
      </svg>
      <div className="metric-value">{score}</div>
      <span>{label}</span>
    </div>
  );
}

export default function AuditHistory() {
  const { currentUser } = useAuth();
  const [audits, setAudits] = useState([]);
  const [selectedAuditId, setSelectedAuditId] = useState(null);
  const [auditDetails, setAuditDetails] = useState(null);
  const [isLoadingList, setIsLoadingList] = useState(true);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [listError, setListError] = useState('');
  const [detailsError, setDetailsError] = useState('');
  const pollingRef = useRef(null);

  const selectedAudit = useMemo(
    () => audits.find((audit) => audit.id === selectedAuditId),
    [audits, selectedAuditId]
  );

  const fetchAudits = async (silent = false) => {
    if (!silent) setIsLoadingList(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/audits`, {
        headers: { Authorization: `Bearer ${idToken}` },
      });
      if (!response.ok) throw new Error('Không thể tải lịch sử phân tích.');
      setAudits(await response.json());
      setListError('');
    } catch (error) {
      console.error(error);
      setListError('Không thể tải lịch sử phân tích.');
    } finally {
      setIsLoadingList(false);
    }
  };

  const fetchAuditDetails = async (id, silent = false) => {
    if (!silent) setIsLoadingDetails(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/audits/${id}`, {
        headers: { Authorization: `Bearer ${idToken}` },
      });
      if (!response.ok) throw new Error('Không thể tải chi tiết audit.');
      setAuditDetails(await response.json());
      setDetailsError('');
    } catch (error) {
      console.error(error);
      setDetailsError('Không thể tải chi tiết audit này.');
    } finally {
      if (!silent) setIsLoadingDetails(false);
    }
  };

  useEffect(() => {
    queueMicrotask(() => fetchAudits());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    queueMicrotask(() => {
      if (selectedAuditId) fetchAuditDetails(selectedAuditId);
      else setAuditDetails(null);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedAuditId]);

  useEffect(() => {
    const hasRunningAudit = audits.some((audit) => [0, 1, 'Pending', 'Processing'].includes(audit.status));
    const currentRunning = auditDetails && [0, 1, 'Pending', 'Processing'].includes(auditDetails.status);

    if (hasRunningAudit || currentRunning) {
      pollingRef.current = setInterval(() => {
        fetchAudits(true);
        if (selectedAuditId) fetchAuditDetails(selectedAuditId, true);
      }, 4000);
    }

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [audits, auditDetails, selectedAuditId]);

  return (
    <section className="feature-page audit-page">
      <div className="page-hero compact-hero">
        <div>
          <span className="eyebrow"><History size={14} /> SEO Audit History</span>
          <h1>Audit History</h1>
          <p>Lịch sử audit, trạng thái xử lý, score và issue được gom về trang riêng này.</p>
        </div>
        <div className="hero-actions">
          <Link className="ghost-action" to="/seo-audit"><Plus size={16} /> Tạo audit mới</Link>
        </div>
      </div>

      <div className="history-workspace">
        <aside className="panel history-index">
          <div className="panel-toolbar">
            <div>
              <h2>Danh sách audit</h2>
              <p>{audits.length} bản ghi</p>
            </div>
            <button className="icon-button" type="button" onClick={() => fetchAudits(true)} title="Làm mới">
              <RefreshCw size={15} />
            </button>
          </div>

          <div className="history-list">
            {isLoadingList ? (
              <div className="empty-state">Đang tải lịch sử phân tích...</div>
            ) : listError ? (
              <div className="notice error"><AlertCircle size={16} />{listError}</div>
            ) : audits.length === 0 ? (
              <div className="empty-state">Chưa có audit nào.</div>
            ) : (
              audits.map((audit) => {
                const [label, className] = getStatus(audit.status);
                return (
                  <button className={`history-row ${selectedAuditId === audit.id ? 'active' : ''}`} key={audit.id} type="button" onClick={() => setSelectedAuditId(audit.id)}>
                    <span>
                      <strong>{audit.keyword}</strong>
                      <small>{audit.url}</small>
                    </span>
                    <span className="row-meta">
                      <span className={`status-badge ${className}`}>{label}</span>
                      <ArrowRight size={16} />
                    </span>
                  </button>
                );
              })
            )}
          </div>
        </aside>

        <div className="panel content-panel">
          <div className="panel-toolbar">
            <div>
              <h2>{selectedAuditId ? 'Audit Detail' : 'Chưa chọn audit'}</h2>
              <p>{selectedAuditId ? selectedAudit?.url || auditDetails?.url : 'Chọn một bản ghi bên trái để xem chi tiết.'}</p>
            </div>
          </div>

          {!selectedAuditId ? (
            <div className="empty-state">Chọn audit trong danh sách để xem score và issue.</div>
          ) : (
            <div className="detail-surface">
              {isLoadingDetails ? (
                <div className="empty-state">Đang tải chi tiết audit...</div>
              ) : detailsError ? (
                <div className="notice error"><AlertCircle size={16} />{detailsError}</div>
              ) : auditDetails ? (
                <>
                  <div className="detail-title-row">
                    <div>
                      <h3>{auditDetails.keyword}</h3>
                      <a href={auditDetails.url} target="_blank" rel="noreferrer">
                        {auditDetails.url} <ExternalLink size={13} />
                      </a>
                    </div>
                    <span className={`status-badge ${getStatus(auditDetails.status)[1]}`}>{getStatus(auditDetails.status)[0]}</span>
                  </div>

                  <div className="detail-meta">
                    <span><Calendar size={14} />{new Date(auditDetails.createdAt).toLocaleString('vi-VN')}</span>
                    <span>{auditDetails.country?.toUpperCase()}</span>
                    <span>{auditDetails.language?.toUpperCase()}</span>
                  </div>

                  {[0, 1, 'Pending', 'Processing'].includes(auditDetails.status) ? (
                    <div className="processing-card">
                      <RefreshCw className="spin" size={24} />
                      <strong>Đang crawl và phân tích dữ liệu SEO</strong>
                      <span>Kết quả sẽ tự động cập nhật sau vài giây.</span>
                    </div>
                  ) : auditDetails.report ? (
                    <>
                      <div className="metrics-grid">
                        <ScoreRing value={auditDetails.report.seoScore} label="SEO tổng thể" tone="blue" />
                        <ScoreRing value={auditDetails.report.technicalScore} label="Kỹ thuật" tone="green" />
                        <ScoreRing value={auditDetails.report.onPageScore} label="On-page" tone="pink" />
                      </div>

                      <div className="issues-list">
                        <div className="section-label"><FileText size={16} /> Vấn đề cần cải thiện ({auditDetails.report.issues?.length || 0})</div>
                        {auditDetails.report.issues?.length ? auditDetails.report.issues.map((issue) => {
                          const severity = issue.severity?.toLowerCase();
                          const high = severity === 'high' || severity === 'critical';
                          const medium = severity === 'medium' || severity === 'warning';
                          return (
                            <article className="issue-card" key={issue.id}>
                              <div>
                                {high ? <AlertCircle size={18} /> : medium ? <AlertTriangle size={18} /> : <Info size={18} />}
                                <strong>{issue.title}</strong>
                              </div>
                              {issue.description && <p>{issue.description}</p>}
                              {issue.recommendation && <footer>{issue.recommendation}</footer>}
                            </article>
                          );
                        }) : (
                          <div className="success-state"><CheckCircle2 size={24} /> Không tìm thấy lỗi SEO quan trọng.</div>
                        )}
                      </div>
                    </>
                  ) : (
                    <div className="empty-state">Không tìm thấy báo cáo cho audit này.</div>
                  )}
                </>
              ) : null}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
