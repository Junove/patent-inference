import { useQuery } from '@tanstack/react-query'
import { apiClient } from './client.ts'

export function useHealthQuery() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/api/v1/health')
      if (error || !data) throw new Error('Health check failed')
      return data
    },
    refetchInterval: 15_000,
  })
}
