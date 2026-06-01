import { apiGet } from './httpClient';
import type { ProjectSummary } from '../types/project';

export function getProjects() {
  return apiGet<ProjectSummary[]>('/api/projects');
}
