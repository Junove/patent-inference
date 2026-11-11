/**
 * Stable references to the operations declared in `contract/openapi.yaml`.
 * Keep these in sync with the OpenAPI document; the generated client in the
 * frontend is produced from the same file.
 */

export const OPENAPI_VERSION = '3.0.3' as const

export const API_PATHS = {
  health: '/health',
  patents: '/patents',
} as const

export type ApiPath = (typeof API_PATHS)[keyof typeof API_PATHS]

export interface HealthResponse {
  status: 'ok'
}

export interface PatentQuery {
  question: string
}

export interface PatentQueryResult {
  id: string
  answer: string
}
