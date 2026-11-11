import { useEffect, useRef, useState } from 'react'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import IconButton from '@mui/material/IconButton'
import List from '@mui/material/List'
import ListItem from '@mui/material/ListItem'
import ListItemText from '@mui/material/ListItemText'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useNavigate, useParams } from 'react-router-dom'
import { useJobStream } from '../api/jobEvents.ts'
import {
  documentDownloadUrl,
  useCancelJobMutation,
  useDeleteFileMutation,
  useGenerateMutation,
  useProjectFilesQuery,
  useProjectsQuery,
  useRegenerateSectionMutation,
  useUploadFileMutation,
} from '../api/projects.ts'
import { EmptyState, ErrorState, LoadingState } from '../components/StateViews.tsx'

const STATUS_COLOR = {
  idle: 'default',
  queued: 'default',
  running: 'info',
  succeeded: 'success',
  failed: 'error',
  cancelled: 'warning',
} as const

export function GeneratorProjectPage() {
  const { projectId = '' } = useParams()
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)

  const projectsQuery = useProjectsQuery()
  const filesQuery = useProjectFilesQuery(projectId)
  const uploadFile = useUploadFileMutation(projectId)
  const deleteFile = useDeleteFileMutation(projectId)
  const generate = useGenerateMutation(projectId)
  const regenerateSection = useRegenerateSectionMutation(projectId)
  const cancelJob = useCancelJobMutation()

  const [instructions, setInstructions] = useState('')
  const [jobId, setJobId] = useState<string | null>(null)
  const [sections, setSections] = useState<Record<string, string>>({})
  const [sectionErrors, setSectionErrors] = useState<Record<string, string>>({})
  const [documentVersion, setDocumentVersion] = useState<number | null>(null)

  const jobStream = useJobStream(jobId)
  const project = projectsQuery.data?.find((p) => p.id === projectId)

  useEffect(() => {
    if (Object.keys(jobStream.sections).length > 0) {
      setSections((prev) => ({ ...prev, ...jobStream.sections }))
    }
  }, [jobStream.sections])

  useEffect(() => {
    if (Object.keys(jobStream.sectionErrors).length > 0) {
      setSectionErrors((prev) => ({ ...prev, ...jobStream.sectionErrors }))
    }
  }, [jobStream.sectionErrors])

  useEffect(() => {
    if (jobStream.documentVersion !== null) {
      setDocumentVersion(jobStream.documentVersion)
    }
  }, [jobStream.documentVersion])

  async function handleRun() {
    try {
      const { job_id } = await generate.mutateAsync(instructions)
      setJobId(job_id)
    } catch {
      // surfaced below via generate.isError/.error
    }
  }

  async function handleRegenerate(name: string) {
    try {
      const { job_id } = await regenerateSection.mutateAsync({ name, instructions })
      setJobId(job_id)
    } catch {
      // surfaced below via regenerateSection.isError/.error
    }
  }

  async function handleSendToLinter() {
    if (documentVersion === null) return
    const response = await fetch(documentDownloadUrl(projectId, documentVersion))
    const blob = await response.blob()
    const file = new File([blob], `${project?.name ?? 'generated'}.docx`, { type: blob.type })
    navigate('/linter', { state: { file } })
  }

  const isRunning = jobStream.status === 'queued' || jobStream.status === 'running'

  if (projectsQuery.isPending) return <LoadingState label="Loading project…" />
  if (!project) return <ErrorState message="Project not found." />

  return (
    <Stack spacing={3} sx={{ maxWidth: 760 }}>
      <Box>
        <Typography variant="h4" component="h1">
          {project.name}
        </Typography>
        <Typography color="text.secondary">{project.description}</Typography>
      </Box>

      <Box>
        <Typography variant="h6">Source files</Typography>
        <Button onClick={() => inputRef.current?.click()} sx={{ mb: 1 }}>
          Add file
        </Button>
        <input
          ref={inputRef}
          type="file"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) uploadFile.mutate(file)
            e.target.value = ''
          }}
        />
        {filesQuery.isPending && <LoadingState label="Loading files…" />}
        {filesQuery.data?.length === 0 && <EmptyState message="No files attached yet." />}
        <List dense>
          {filesQuery.data?.map((file) => (
            <ListItem
              key={file.id}
              secondaryAction={
                <IconButton edge="end" aria-label="delete" onClick={() => deleteFile.mutate(file.id)}>
                  ✕
                </IconButton>
              }
            >
              <ListItemText primary={file.filename} secondary={`${file.size} bytes`} />
            </ListItem>
          ))}
        </List>
      </Box>

      <TextField
        label="Instructions"
        value={instructions}
        onChange={(e) => setInstructions(e.target.value)}
        multiline
        minRows={3}
      />

      <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
        <Button variant="contained" onClick={handleRun} disabled={isRunning || generate.isPending}>
          Generate
        </Button>
        {isRunning && (
          <Button
            color="warning"
            onClick={() => jobId && cancelJob.mutate(jobId, { onSuccess: () => jobStream.cancel() })}
          >
            Cancel
          </Button>
        )}
        {jobStream.status !== 'idle' && (
          <Chip
            label={jobStream.status}
            color={STATUS_COLOR[jobStream.status]}
            size="small"
            sx={{ textTransform: 'capitalize' }}
          />
        )}
      </Stack>
      {jobStream.error && <ErrorState message={jobStream.error} />}
      {generate.isError && <ErrorState message="Failed to start generation. Check the backend connection." />}
      {regenerateSection.isError && (
        <ErrorState message="Failed to regenerate that section. Check the backend connection." />
      )}

      {Object.keys(sections).length > 0 && (
        <Stack spacing={2}>
          <Typography variant="h6">Draft sections</Typography>
          {Object.entries(sections).map(([name, content]) => (
            <Box key={name} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 2 }}>
              <Typography variant="subtitle1" sx={{ textTransform: 'capitalize' }}>
                {name}
              </Typography>
              <Typography color="text.secondary" sx={{ whiteSpace: 'pre-wrap', mb: 1 }}>
                {content || (isRunning ? 'Drafting…' : '')}
              </Typography>
              {sectionErrors[name] && <ErrorState message={sectionErrors[name]} />}
              <Button
                size="small"
                disabled={isRunning || regenerateSection.isPending}
                onClick={() => handleRegenerate(name)}
              >
                Regenerate this section
              </Button>
            </Box>
          ))}
        </Stack>
      )}

      {documentVersion !== null && (
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            component="a"
            href={documentDownloadUrl(projectId, documentVersion)}
            download={`${project.name}.docx`}
          >
            Download .docx
          </Button>
          <Button variant="outlined" onClick={handleSendToLinter}>
            Send to linter
          </Button>
        </Stack>
      )}
    </Stack>
  )
}
