import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Copy,
  FileJson,
  History,
  Plus,
  RefreshCw,
  Terminal,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5001';

const statusLabels = {
  Pending: ['Chờ hàng đợi', 'pending'],
  Running: ['Đang chạy', 'processing'],
  Success: ['Thành công', 'completed'],
  Completed: ['Hoàn thành', 'completed'],
  Failed: ['Thất bại', 'failed'],
  RequiresManualAction: ['Cần thao tác', 'warning'],
};

function getStatus(status) {
  return statusLabels[status] ?? [status || 'Không rõ', 'failed'];
}

function JobDetails({ job, isLoading, error }) {
  const [expanded, setExpanded] = useState(null);
  const [copied, setCopied] = useState(null);

  if (isLoading) return <div className="empty-state">Đang tải tiến trình submit...</div>;
  if (error) return <div className="notice error"><AlertCircle size={16} />{error}</div>;
  if (!job) return <div className="empty-state">Chọn job bên trái để xem tiến trình.</div>;

  return (
    <div className="job-detail standalone">
      <div className="detail-title-row">
        <div>
          <h3>{job.websiteUrl}</h3>
          <span>Tạo lúc {new Date(job.createdAt).toLocaleString('vi-VN')}</span>
        </div>
        <span className={`status-badge ${getStatus(job.status)[1]}`}>{getStatus(job.status)[0]}</span>
      </div>

      <div className="job-platform-list">
        {job.details?.map((detail) => {
          const isOpen = expanded === detail.detailId;
          return (
            <article className="job-platform-card" key={detail.detailId}>
              <button type="button" onClick={() => setExpanded(isOpen ? null : detail.detailId)}>
                <span>
                  <strong>{detail.platformName}</strong>
                  <small>{detail.platformCode?.toUpperCase()}</small>
                </span>
                <span>
                  <span className={`status-badge ${getStatus(detail.status)[1]}`}>{getStatus(detail.status)[0]}</span>
                  {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </span>
              </button>

              {isOpen && (
                <div className="job-log-surface">
                  {detail.errorMessage && <div className="notice error"><AlertCircle size={16} />{detail.errorMessage}</div>}
                  {detail.responseData && (
                    <div className="response-box">
                      <div>
                        <FileJson size={14} />
                        Response Data
                        <button
                          type="button"
                          onClick={() => {
                            navigator.clipboard.writeText(detail.responseData);
                            setCopied(detail.detailId);
                            setTimeout(() => setCopied(null), 1800);
                          }}
                        >
                          <Copy size={13} /> {copied === detail.detailId ? 'Copied' : 'Copy'}
                        </button>
                      </div>
                      <pre>{detail.responseData}</pre>
                    </div>
                  )}
                  <div className="terminal-box">
                    <div><Terminal size={14} /> Nhật ký hoạt động</div>
                    {detail.auditLogs?.length ? detail.auditLogs.map((log) => (
                      <p key={log.id}>
                        <span>[{new Date(log.timestamp).toLocaleTimeString('vi-VN')}] {log.action} ({log.status})</span>
                        {log.logContent && <small>{log.logContent}</small>}
                      </p>
                    )) : <p><span>Chưa có log.</span></p>}
                  </div>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}

export default function SubmitHistory() {
  const { currentUser } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const [isLoadingJobDetails, setIsLoadingJobDetails] = useState(false);
  const [jobsError, setJobsError] = useState('');
  const [jobDetailsError, setJobDetailsError] = useState('');
  const pollingRef = useRef(null);

  const fetchJobs = async (silent = false) => {
    if (!silent) setIsLoadingJobs(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/history`, {
        headers: { Authorization: `Bearer ${idToken}` },
      });
      if (!response.ok) throw new Error('Không thể tải lịch sử submit.');
      setJobs(await response.json());
      setJobsError('');
    } catch (error) {
      console.error(error);
      setJobsError('Không thể tải lịch sử submit.');
    } finally {
      setIsLoadingJobs(false);
    }
  };

  const fetchJobDetails = async (id, silent = false) => {
    if (!silent) setIsLoadingJobDetails(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/jobs/${id}`, {
        headers: { Authorization: `Bearer ${idToken}` },
      });
      if (!response.ok) throw new Error('Không thể tải tiến trình job.');
      setJobDetails(await response.json());
      setJobDetailsError('');
    } catch (error) {
      console.error(error);
      setJobDetailsError('Không thể tải tiến trình job.');
    } finally {
      if (!silent) setIsLoadingJobDetails(false);
    }
  };

  useEffect(() => {
    queueMicrotask(() => fetchJobs());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    queueMicrotask(() => {
      if (selectedJobId) fetchJobDetails(selectedJobId);
      else setJobDetails(null);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedJobId]);

  useEffect(() => {
    const hasRunning = jobs.some((job) => ['Pending', 'Running'].includes(job.status));
    const currentRunning = jobDetails && ['Pending', 'Running'].includes(jobDetails.status);
    if (hasRunning || currentRunning) {
      pollingRef.current = setInterval(() => {
        fetchJobs(true);
        if (selectedJobId) fetchJobDetails(selectedJobId, true);
      }, 3000);
    }
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobs, jobDetails, selectedJobId]);

  return (
    <section className="feature-page submit-page">
      <div className="page-hero compact-hero">
        <div>
          <span className="eyebrow"><History size={14} /> Submit Job History</span>
          <h1>Submit History</h1>
          <p>Lịch sử submit và log từng platform được tách khỏi màn hình chọn platform.</p>
        </div>
        <div className="hero-actions">
          <Link className="ghost-action" to="/submit-website"><Plus size={16} /> Submit platform mới</Link>
        </div>
      </div>

      <div className="history-workspace">
        <aside className="panel history-index">
          <div className="panel-toolbar">
            <div>
              <h2>Submit jobs</h2>
              <p>{jobs.length} bản ghi</p>
            </div>
            <button className="icon-button" type="button" onClick={() => fetchJobs(true)} title="Làm mới">
              <RefreshCw size={15} />
            </button>
          </div>

          {isLoadingJobs ? (
            <div className="empty-state small">Đang tải lịch sử...</div>
          ) : jobsError ? (
            <div className="notice error"><AlertCircle size={16} />{jobsError}</div>
          ) : jobs.length === 0 ? (
            <div className="empty-state small">Chưa có job submit.</div>
          ) : (
            <div className="job-list expanded">
              {jobs.map((job) => (
                <button
                  className={selectedJobId === job.jobId ? 'active' : ''}
                  key={job.jobId}
                  type="button"
                  onClick={() => setSelectedJobId(selectedJobId === job.jobId ? null : job.jobId)}
                >
                  <span>
                    <strong>{job.websiteUrl}</strong>
                    <small>{job.details?.map((detail) => detail.platformName).join(', ') || 'N/A'}</small>
                  </span>
                  <span className={`status-dot ${getStatus(job.status)[1]}`} />
                </button>
              ))}
            </div>
          )}
        </aside>

        <div className="panel content-panel">
          <JobDetails job={jobDetails} isLoading={isLoadingJobDetails} error={jobDetailsError} />
        </div>
      </div>
    </section>
  );
}
