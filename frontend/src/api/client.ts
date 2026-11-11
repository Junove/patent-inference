import createClient from 'openapi-fetch'
import type { paths } from './schema'

export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

/**
 * Typed API client generated from `contract/openapi.yaml`.
 * Regenerate the schema types with `npm run generate:api`.
 */
export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
})
