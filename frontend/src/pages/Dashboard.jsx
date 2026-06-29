import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertCircle,
  BarChart3,
  CheckCircle2,
  Flag,
  Globe2,
  History,
  KeyRound,
  Languages,
  RefreshCw,
  Search,
  ShieldCheck,
  Zap,
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

export default function Dashboard() {
  const { currentUser } = useAuth();
  const [url, setUrl] = useState('');
  const [keyword, setKeyword] = useState('');
  const [country, setCountry] = useState('vn');
  const [language, setLanguage] = useState('vi');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formMessage, setFormMessage] = useState(null);
  const [audits, setAudits] = useState([]);

  const fetchAuditStats = async () => {
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/audits`, {
        headers: { Authorization: `Bearer ${idToken}` },
      });
      if (response.ok) setAudits(await response.json());
    } catch (error) {
      console.error(error);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setFormMessage(null);

    if (!url || !keyword) {
      setFormMessage({ type: 'error', text: 'Vui lòng nhập URL và từ khóa mục tiêu.' });
      return;
    }

    try {
      new URL(url);
    } catch {
      setFormMessage({ type: 'error', text: 'URL chưa hợp lệ. Hãy nhập dạng https://example.com.' });
      return;
    }

    setIsSubmitting(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/audits`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify({ url, keyword, country, language }),
      });
      if (!response.ok) throw new Error('Yêu cầu phân tích thất bại.');
      setFormMessage({ type: 'success', text: 'Đã gửi yêu cầu phân tích. Mở trang lịch sử để theo dõi tiến trình.' });
      setUrl('');
      setKeyword('');
      fetchAuditStats();
    } catch (error) {
      setFormMessage({ type: 'error', text: error.message || 'Có lỗi khi tạo audit.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    queueMicrotask(() => fetchAuditStats());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="feature-page audit-page">
      <div className="page-hero">
        <div>
          <span className="eyebrow"><Zap size={14} /> Realtime SEO intelligence</span>
          <h1>SEO Audit</h1>
          <p>Trang này chỉ dành cho thao tác tạo audit mới. Lịch sử và chi tiết kết quả được tách sang một trang riêng.</p>
        </div>
        <div className="hero-stats">
          <div><strong>{audits.length}</strong><span>Audits</span></div>
          <div><strong>{audits.filter((audit) => getStatus(audit.status)[1] === 'completed').length}</strong><span>Completed</span></div>
          <div><strong>{audits.filter((audit) => ['pending', 'processing'].includes(getStatus(audit.status)[1])).length}</strong><span>Running</span></div>
        </div>
      </div>

      <div className="audit-workspace single-workspace">
        <aside className="panel command-panel">
          <div className="panel-heading">
            <ShieldCheck size={18} />
            <div>
              <h2>New Analysis</h2>
              <p>Nhập URL và keyword để bắt đầu audit.</p>
            </div>
          </div>

          {formMessage && (
            <div className={`notice ${formMessage.type}`}>
              {formMessage.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
              {formMessage.text}
            </div>
          )}

          <form className="modern-form" onSubmit={handleSubmit}>
            <label>
              <span>Website URL</span>
              <div className="field-shell">
                <Globe2 size={18} />
                <input value={url} onChange={(event) => setUrl(event.target.value)} placeholder="https://example.com/bai-viet" />
              </div>
            </label>
            <label>
              <span>Keyword mục tiêu</span>
              <div className="field-shell">
                <KeyRound size={18} />
                <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="thiết kế web chuẩn SEO" />
              </div>
            </label>
            <div className="form-grid-2">
              <label>
                <span>Quốc gia</span>
                <div className="field-shell">
                  <Flag size={18} />
                  <select value={country} onChange={(event) => setCountry(event.target.value)}>
                    <option value="vn">Việt Nam</option>
                    <option value="us">Hoa Kỳ</option>
                    <option value="jp">Nhật Bản</option>
                    <option value="sg">Singapore</option>
                  </select>
                </div>
              </label>
              <label>
                <span>Ngôn ngữ</span>
                <div className="field-shell">
                  <Languages size={18} />
                  <select value={language} onChange={(event) => setLanguage(event.target.value)}>
                    <option value="vi">Tiếng Việt</option>
                    <option value="en">English</option>
                    <option value="ja">日本語</option>
                  </select>
                </div>
              </label>
            </div>
            <button className="primary-action" disabled={isSubmitting} type="submit">
              {isSubmitting ? <RefreshCw className="spin" size={18} /> : <Search size={18} />}
              Bắt đầu phân tích
            </button>
          </form>
        </aside>

        <div className="panel content-panel action-panel">
          <div className="panel-heading">
            <BarChart3 size={18} />
            <div>
              <h2>Audit history moved</h2>
              <p>Xem danh sách audit, trạng thái xử lý, điểm SEO và issue trong trang lịch sử riêng.</p>
            </div>
          </div>
          <Link className="primary-action link-action" to="/seo-audit/history">
            <History size={18} />
            Mở lịch sử SEO Audit
          </Link>
        </div>
      </div>
    </section>
  );
}
