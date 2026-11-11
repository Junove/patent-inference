import { describe, expect, it } from 'vitest'
import {
  API_PATHS,
  OPENAPI_VERSION,
  type HealthResponse,
  type PatentQuery,
  type PatentQueryResult,
} from './index'

describe('API contract constants', () => {
  it('targets the OpenAPI 3.0.3 document', () => {
    expect(OPENAPI_VERSION).toBe('3.0.3')
  })

  it('exposes the documented paths', () => {
    expect(API_PATHS.health).toBe('/health')
    expect(API_PATHS.patents).toBe('/patents')
  })

  it('keeps response shapes aligned with the contract', () => {
    const health: HealthResponse = { status: 'ok' }
    const query: PatentQuery = { question: 'What is a patent?' }
    const result: PatentQueryResult = { id: 'abc', answer: 'A patent is…' }

    expect(health.status).toBe('ok')
    expect(query.question).not.toHaveLength(0)
    expect(result.id).toBe('abc')
  })
})
