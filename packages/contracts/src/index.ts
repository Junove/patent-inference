/**
 * Stable references to the operations declared in `contract/openapi.yaml`.
 * Keep these in sync with the OpenAPI document; the generated client in the
 * frontend is produced from the same file.
 */

export const OPENAPI_VERSION = '3.1.0' as const

export const API_PATHS = {
  health: '/api/v1/health',
  projects: '/api/v1/projects',
  patentsSearch: '/api/v1/patents/search',
  lint: '/api/v1/lint',
} as const

export type ApiPath = (typeof API_PATHS)[keyof typeof API_PATHS]

export function patentPath(patentId: string): string {
  return `/api/v1/patents/${encodeURIComponent(patentId)}`
}

export function projectFilesPath(projectId: string): string {
  return `/api/v1/projects/${encodeURIComponent(projectId)}/files`
}

export function projectGeneratePath(projectId: string): string {
  return `/api/v1/projects/${encodeURIComponent(projectId)}/generate`
}

export function jobEventsPath(jobId: string): string {
  return `/api/v1/jobs/${encodeURIComponent(jobId)}/events`
}

export function jobCancelPath(jobId: string): string {
  return `/api/v1/jobs/${encodeURIComponent(jobId)}/cancel`
}

export interface HealthResponse {
  status: 'ok'
  version: string
}

export interface PatentSummary {
  id: string
  title: string
  abstract: string
  assignee?: string | null
  filing_date?: string | null
}

export interface SearchResults {
  results: PatentSummary[]
  total: number
}
