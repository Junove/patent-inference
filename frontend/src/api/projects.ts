import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { API_BASE_URL, apiClient } from './client.ts'
import type { components } from './schema'

type UploadFileBody = components['schemas']['Body_upload_file_api_v1_projects__project_id__files_post']

export function useProjectsQuery() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/api/v1/projects')
      if (error || !data) throw new Error('Failed to list projects')
      return data
    },
  })
}

export function useCreateProjectMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (input: { name: string; description: string }) => {
      const { data, error } = await apiClient.POST('/api/v1/projects', { body: input })
      if (error || !data) throw new Error('Failed to create project')
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects'] }),
  })
}

export function useProjectFilesQuery(projectId: string) {
  return useQuery({
    queryKey: ['projects', projectId, 'files'],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/api/v1/projects/{project_id}/files', {
        params: { path: { project_id: projectId } },
      })
      if (error || !data) throw new Error('Failed to list files')
      return data
    },
  })
}

export function useUploadFileMutation(projectId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData()
      form.append('file', file)
      const { data, error } = await apiClient.POST('/api/v1/projects/{project_id}/files', {
        params: { path: { project_id: projectId } },
        body: form as unknown as UploadFileBody,
      })
      if (error || !data) throw new Error('Upload failed')
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'files'] }),
  })
}

export function useDeleteFileMutation(projectId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (fileId: string) => {
      const { error } = await apiClient.DELETE('/api/v1/projects/{project_id}/files/{file_id}', {
        params: { path: { project_id: projectId, file_id: fileId } },
      })
      if (error) throw new Error('Delete failed')
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'files'] }),
  })
}

export function useGenerateMutation(projectId: string) {
  return useMutation({
    mutationFn: async (instructions: string) => {
      const { data, error } = await apiClient.POST('/api/v1/projects/{project_id}/generate', {
        params: { path: { project_id: projectId } },
        body: { instructions },
      })
      if (error || !data) throw new Error('Failed to start generation')
      return data
    },
  })
}

export function useRegenerateSectionMutation(projectId: string) {
  return useMutation({
    mutationFn: async ({ name, instructions }: { name: string; instructions: string }) => {
      const { data, error } = await apiClient.POST(
        '/api/v1/projects/{project_id}/sections/{name}/regenerate',
        {
          params: { path: { project_id: projectId, name } },
          body: { instructions },
        },
      )
      if (error || !data) throw new Error('Failed to regenerate section')
      return data
    },
  })
}

export function useCancelJobMutation() {
  return useMutation({
    mutationFn: async (jobId: string) => {
      const { data, error } = await apiClient.POST('/api/v1/jobs/{job_id}/cancel', {
        params: { path: { job_id: jobId } },
      })
      if (error || !data) throw new Error('Failed to cancel job')
      return data
    },
  })
}

export function documentDownloadUrl(projectId: string, version: number): string {
  return `${API_BASE_URL}/api/v1/projects/${projectId}/documents/${version}`
}
