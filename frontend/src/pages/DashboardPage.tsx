import { PageHeader } from '../components/PageHeader';

export function DashboardPage() {
  return (
    <section>
      <PageHeader
        title="Dashboard"
        description="Overview of projects, audits, keyword movement, and technical SEO health."
      />

      <div className="metric-grid">
        <article className="metric-card">
          <span className="metric-label">Projects</span>
          <strong className="metric-value">0</strong>
        </article>
        <article className="metric-card">
          <span className="metric-label">Open Issues</span>
          <strong className="metric-value">0</strong>
        </article>
        <article className="metric-card">
          <span className="metric-label">Tracked Keywords</span>
          <strong className="metric-value">0</strong>
        </article>
      </div>
    </section>
  );
}
