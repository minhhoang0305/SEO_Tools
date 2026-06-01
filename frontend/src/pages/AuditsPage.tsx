import { PageHeader } from '../components/PageHeader';

export function AuditsPage() {
  return (
    <section>
      <PageHeader
        title="Audits"
        description="Review crawl runs, technical checks, and generated recommendations."
      />

      <div className="empty-state">
        <h2>No audit runs</h2>
        <p>Audit history will appear after a project crawl is started.</p>
      </div>
    </section>
  );
}
