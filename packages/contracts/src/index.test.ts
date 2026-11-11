import { describe, expect, it } from 'vitest'
import {
  API_PATHS,
  OPENAPI_VERSION,
  jobCancelPath,
  jobEventsPath,
  patentPath,
  projectFilesPath,
  type HealthResponse,
  type PatentSummary,
  type SearchResults,
} from './index'

describe('API contract constants', () => {
  it('targets the OpenAPI 3.1 document', () => {
    expect(OPENAPI_VERSION).toBe('3.1.0')
  })

  it('exposes the documented paths', () => {
    expect(API_PATHS.health).toBe('/api/v1/health')
    expect(API_PATHS.projects).toBe('/api/v1/projects')
    expect(API_PATHS.patentsSearch).toBe('/api/v1/patents/search')
    expect(API_PATHS.lint).toBe('/api/v1/lint')
  })

  it('builds parameterized paths safely', () => {
    expect(patentPath('abc 123')).toBe('/api/v1/patents/abc%20123')
    expect(projectFilesPath('p1')).toBe('/api/v1/projects/p1/files')
    expect(jobEventsPath('j1')).toBe('/api/v1/jobs/j1/events')
    expect(jobCancelPath('j1')).toBe('/api/v1/jobs/j1/cancel')
  })

  it('keeps response shapes aligned with the contract', () => {
    const health: HealthResponse = { status: 'ok', version: '0.1.0' }
    const patent: PatentSummary = {
      id: 'US-1',
      title: 'A patent',
      abstract: 'An abstract',
    }
    const results: SearchResults = { results: [patent], total: 1 }

    expect(health.version).toBe('0.1.0')
    expect(results.results[0]?.id).toBe('US-1')
    expect(results.total).toBe(1)
  })
})
