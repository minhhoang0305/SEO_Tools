import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  ExternalLink,
  FileJson,
  Filter,
  Globe2,
  History,
  Lock,
  RefreshCw,
  Search,
  Send,
  Upload,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getPlatformBlueprint, normalizePlatformCode } from '../data/platformBlueprints';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5001';

function buildPlatformSlug(platform) {
  return normalizePlatformCode(platform.code);
}

function toPayload(formData, platformId, blueprint) {
  const payload = {
    ...formData,
    websiteUrl: formData.url,
    platformIds: [platformId],
  };

  if (blueprint.title === 'Awesome Indie') {
    payload.description = formData.description;
    payload.categories = formData.categories;
    payload.AwesomeIndieDebugHeadful = true;
  }

  if (blueprint.title === '10words') {
    payload.category = formData.tenWordsCategory;
  }

  if (blueprint.title === 'BAI.tools') {
    payload.BAIToolsUseApi = true;
    payload.BAIToolsPlanIndex = 0;
    payload.BAIToolsLocale = 'en';
  }

  if (blueprint.title === 'Future Tools') {
    payload.newsletterOptIn = formData.newsletterOptIn ? 'true' : undefined;
  }

  if (blueprint.title === 'Alternative') {
    payload.homepageUrl = formData.url;
  }

  Object.keys(payload).forEach((key) => {
    if (payload[key] === '' || payload[key] === null) delete payload[key];
  });

  return payload;
}

function PlatformField({ field, value, onChange }) {
  const id = `field-${field.name}`;

  if (field.type === 'checkbox') {
    return (
      <label className="checkbox-field" htmlFor={id}>
        <input id={id} type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(field.name, event.target.checked)} />
        <span>{field.label}</span>
      </label>
    );
  }

  return (
    <label className={field.type === 'textarea' ? 'wide-field' : ''} htmlFor={id}>
      <span>{field.label}{field.required ? ' *' : ''}</span>
      <div className="field-shell clean">
        {field.type === 'textarea' ? (
          <textarea
            id={id}
            rows={4}
            value={value ?? ''}
            required={field.required}
            placeholder={field.placeholder}
            onChange={(event) => onChange(field.name, event.target.value)}
          />
        ) : field.type === 'select' ? (
          <select id={id} value={value ?? ''} required={field.required} onChange={(event) => onChange(field.name, event.target.value)}>
            {field.options.map((option) => <option key={option} value={option}>{option}</option>)}
          </select>
        ) : (
          <input
            id={id}
            type={field.type}
            value={value ?? ''}
            required={field.required}
            placeholder={field.placeholder}
            onChange={(event) => onChange(field.name, event.target.value)}
          />
        )}
      </div>
    </label>
  );
}

export default function SubmitWebsite() {
  const { platformCode } = useParams();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [platforms, setPlatforms] = useState([]);
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(true);
  const [message, setMessage] = useState(null);
  const [query, setQuery] = useState('');
  const [method, setMethod] = useState('ALL');
  const [formData, setFormData] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sessionFile, setSessionFile] = useState(null);

  const activePlatform = useMemo(() => {
    if (!platformCode) return null;
    const normalizedParam = normalizePlatformCode(platformCode);
    return platforms.find((platform) => normalizePlatformCode(platform.code) === normalizedParam);
  }, [platforms, platformCode]);

  const activeBlueprint = getPlatformBlueprint(activePlatform?.code ?? platformCode);

  const filteredPlatforms = useMemo(() => {
    return platforms.filter((platform) => {
      const searchTarget = `${platform.name} ${platform.code}`.toLowerCase();
      const matchesQuery = searchTarget.includes(query.toLowerCase());
      const matchesMethod = method === 'ALL' || (method === 'API' ? platform.submitMethod === 'API' : platform.submitMethod !== 'API');
      return matchesQuery && matchesMethod;
    });
  }, [platforms, query, method]);

  const fetchPlatforms = async () => {
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/platforms`, {
        headers: { Authorization: `Bearer ${idToken}` },
      });
      if (!response.ok) throw new Error('Không thể tải danh sách platform.');
      setPlatforms(await response.json());
      setMessage(null);
    } catch (error) {
      console.error(error);
      setMessage({ type: 'error', text: 'Không thể tải danh sách platform.' });
    } finally {
      setIsLoadingPlatforms(false);
    }
  };

  const handleChange = (name, value) => {
    setFormData((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!activePlatform) return;
    setMessage(null);

    const urlValue = formData.url;
    if (urlValue) {
      try {
        new URL(urlValue);
      } catch {
        setMessage({ type: 'error', text: 'URL chưa hợp lệ. Hãy nhập dạng https://example.com.' });
        return;
      }
    }

    setIsSubmitting(true);
    try {
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify(toPayload(formData, activePlatform.id, activeBlueprint)),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.Message || 'Gửi yêu cầu submit thất bại.');
      }
      setMessage({ type: 'success', text: `Đã gửi job cho ${activePlatform.name}. Mở trang lịch sử để theo dõi tiến trình.` });
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const importSession = async () => {
    if (!activePlatform || !sessionFile) {
      setMessage({ type: 'error', text: 'Vui lòng chọn file storage_state JSON trước.' });
      return;
    }

    try {
      const credentialData = await sessionFile.text();
      const idToken = await currentUser.getIdToken();
      const response = await fetch(`${API_BASE_URL}/api/submit/credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify({ platformId: activePlatform.id, credentialData }),
      });
      if (!response.ok) throw new Error('Không thể import session.');
      setMessage({ type: 'success', text: 'Đã import browser session thành công.' });
      setSessionFile(null);
    } catch (error) {
      setMessage({ type: 'error', text: error.message });
    }
  };

  useEffect(() => {
    queueMicrotask(() => fetchPlatforms());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    queueMicrotask(() => {
      setMessage(null);
      if (activePlatform) {
        const nextBlueprint = getPlatformBlueprint(activePlatform.code);
        setFormData(nextBlueprint.defaults);
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activePlatform?.id]);

  const renderDirectory = () => (
    <>
      <div className="page-hero">
        <div>
          <span className="eyebrow"><Globe2 size={14} /> Platform directory</span>
          <h1>Submit Platforms</h1>
          <p>Mỗi platform là một trang riêng. Chọn site cần submit, app sẽ mở form đúng field yêu cầu.</p>
        </div>
        <div className="hero-actions">
          <Link className="ghost-action" to="/submit-website/history">
            <History size={16} />
            Lịch sử submit
          </Link>
        </div>
      </div>

      <div className="directory-toolbar">
        <div className="search-shell">
          <Search size={16} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Tìm platform..." />
        </div>
        <div className="segmented">
          {['ALL', 'API', 'AUTOMATION'].map((item) => (
            <button className={method === item ? 'active' : ''} key={item} type="button" onClick={() => setMethod(item)}>
              <Filter size={14} /> {item === 'ALL' ? 'Tất cả' : item === 'API' ? 'Direct API' : 'Automation'}
            </button>
          ))}
        </div>
      </div>

      {message && <div className={`notice ${message.type}`}><AlertCircle size={16} />{message.text}</div>}

      {isLoadingPlatforms ? (
        <div className="empty-state">Đang tải platform...</div>
      ) : (
        <div className="platform-grid">
          {filteredPlatforms.map((platform) => {
            const blueprint = getPlatformBlueprint(platform.code);
            const Icon = blueprint.icon;
            return (
              <Link className={`platform-card accent-${blueprint.accent}`} key={platform.id} to={`/submit-website/${buildPlatformSlug(platform)}`}>
                <div>
                  <span className="platform-icon"><Icon size={20} /></span>
                  <span className="method-badge">{platform.submitMethod === 'API' ? 'DIRECT API' : 'AUTOMATION'}</span>
                </div>
                <h2>{platform.name}</h2>
                <p>{blueprint.description}</p>
                <footer>
                  <span>{blueprint.fields.length} fields</span>
                  <ArrowRight size={16} />
                </footer>
              </Link>
            );
          })}
        </div>
      )}
    </>
  );

  const renderPlatformPage = () => {
    if (isLoadingPlatforms) return <div className="empty-state">Đang tải platform...</div>;
    if (!activePlatform) {
      return (
        <div className="empty-state">
          Không tìm thấy platform này.
          <button className="ghost-action" type="button" onClick={() => navigate('/submit-website')}>Quay lại directory</button>
        </div>
      );
    }

    const Icon = activeBlueprint.icon;

    return (
      <>
        <button className="ghost-action back-action" type="button" onClick={() => navigate('/submit-website')}>
          <ArrowLeft size={16} /> Platform directory
        </button>

        <div className={`platform-detail-hero accent-${activeBlueprint.accent}`}>
          <div className="platform-icon xl"><Icon size={28} /></div>
          <div>
            <span>{activeBlueprint.subtitle}</span>
            <h1>{activePlatform.name}</h1>
            <p>{activeBlueprint.description}</p>
            {activePlatform.websiteUrl && (
              <a href={activePlatform.websiteUrl} target="_blank" rel="noreferrer">
                Mở website platform <ExternalLink size={14} />
              </a>
            )}
          </div>
          <span className="method-badge large">{activePlatform.submitMethod === 'API' ? 'DIRECT API' : 'UI AUTOMATION'}</span>
        </div>

        {message && (
          <div className={`notice ${message.type}`}>
            {message.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
            {message.text}
            {message.type === 'success' && (
              <Link className="inline-link" to="/submit-website/history">Xem lịch sử</Link>
            )}
          </div>
        )}

        <div className="platform-form-layout">
          <form className="panel platform-form" onSubmit={handleSubmit}>
            <div className="panel-heading">
              <Send size={18} />
              <div>
                <h2>Required Fields</h2>
                <p>Field bên dưới được map theo platform đang chọn.</p>
              </div>
            </div>

            <div className="dynamic-fields">
              {activeBlueprint.fields.map((field) => (
                <PlatformField key={field.name} field={field} value={formData[field.name]} onChange={handleChange} />
              ))}
            </div>

            {activeBlueprint.supportsSession && (
              <div className="session-import">
                <div>
                  <Lock size={16} />
                  <span>Automation Browser Session</span>
                </div>
                <input type="file" accept=".json,application/json" onChange={(event) => setSessionFile(event.target.files?.[0] ?? null)} />
                <button className="ghost-action" type="button" onClick={importSession}>
                  <Upload size={15} /> Import session
                </button>
              </div>
            )}

            <button className="primary-action" disabled={isSubmitting} type="submit">
              {isSubmitting ? <RefreshCw className="spin" size={18} /> : <Send size={18} />}
              Submit to {activePlatform.name}
            </button>
          </form>

          <aside className="panel payload-panel">
            <div className="panel-heading">
              <FileJson size={18} />
              <div>
                <h2>Payload Preview</h2>
                <p>Dữ liệu sẽ gửi sang worker.</p>
              </div>
            </div>
            <pre>{JSON.stringify(toPayload(formData, activePlatform.id, activeBlueprint), null, 2)}</pre>
          </aside>
        </div>
      </>
    );
  };

  return (
    <section className="feature-page submit-page">
      {platformCode ? renderPlatformPage() : renderDirectory()}
    </section>
  );
}
