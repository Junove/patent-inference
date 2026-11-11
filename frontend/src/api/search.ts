import { useQuery } from '@tanstack/react-query'
import { apiClient } from './client.ts'

export interface SearchFilters {
  q: string
  dateFrom: string
  dateTo: string
  assignee: string
  inventor: string
  classification: string
}

// Matches the backend's fixed search page size (backend/app/search/*.py); the API doesn't expose it.
export const PAGE_SIZE = 10

export const emptyFilters: SearchFilters = {
  q: '',
  dateFrom: '',
  dateTo: '',
  assignee: '',
  inventor: '',
  classification: '',
}

export function useSearchQuery(filters: SearchFilters, page: number, enabled: boolean) {
  return useQuery({
    queryKey: ['patents', 'search', filters, page],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/api/v1/patents/search', {
        params: {
          query: {
            q: filters.q,
            page,
            date_from: filters.dateFrom || undefined,
            date_to: filters.dateTo || undefined,
            assignee: filters.assignee || undefined,
            inventor: filters.inventor || undefined,
            classification: filters.classification || undefined,
          },
        },
      })
      if (error || !data) throw new Error('Search failed')
      return data
    },
    enabled,
  })
}

export function usePatentQuery(patentId: string | null) {
  return useQuery({
    queryKey: ['patents', patentId],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/api/v1/patents/{patent_id}', {
        params: { path: { patent_id: patentId! } },
      })
      if (error || !data) throw new Error('Patent lookup failed')
      return data
    },
    enabled: patentId !== null,
  })
}
