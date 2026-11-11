import { useMutation } from '@tanstack/react-query'
import { apiClient } from './client.ts'
import type { components } from './schema'

type LintBody = components['schemas']['Body_lint_api_v1_lint_post']

export function useLintMutation() {
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData()
      form.append('file', file)
      const { data, error } = await apiClient.POST('/api/v1/lint', {
        body: form as unknown as LintBody,
      })
      if (error || !data) throw new Error('Lint failed')
      return data
    },
  })
}
