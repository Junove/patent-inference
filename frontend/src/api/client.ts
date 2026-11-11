import createClient from 'openapi-fetch'
import type { paths } from './schema'

export const API_BASE_URL_STORAGE_KEY = 'patent-inference:apiBaseUrl'

function readBaseUrl(): string {
  try {
    const stored = localStorage.getItem(API_BASE_URL_STORAGE_KEY)
    if (stored) return stored
  } catch {
    // localStorage unavailable (e.g. private browsing) — fall back to the default.
  }
  return import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
}

export const API_BASE_URL: string = readBaseUrl()

/**
 * Typed API client generated from `contract/openapi.yaml`.
 * Regenerate the schema types with `npm run generate:api`.
 */
export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
})
