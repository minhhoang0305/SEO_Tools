import { Plus } from 'lucide-react';
import { PageHeader } from '../components/PageHeader';

export function ProjectsPage() {
  return (
    <section>
      <PageHeader
        title="Projects"
        description="Manage websites and SEO settings before running crawls and audits."
        action={
          <button className="primary-button" type="button">
            <Plus size={18} aria-hidden="true" />
            <span>New Project</span>
          </button>
        }
      />

      <div className="empty-state">
        <h2>No projects yet</h2>
        <p>Create your first project to start auditing a website.</p>
      </div>
    </section>
  );
}
