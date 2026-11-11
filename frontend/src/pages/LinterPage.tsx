import { useEffect, useRef, useState } from 'react'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import List from '@mui/material/List'
import ListItemButton from '@mui/material/ListItemButton'
import ListItemText from '@mui/material/ListItemText'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { useLocation } from 'react-router-dom'
import { useLintMutation } from '../api/lint.ts'
import { EmptyState, LoadingState } from '../components/StateViews.tsx'

const SEVERITY_COLOR = { error: 'error', warning: 'warning', info: 'info' } as const

export function LinterPage() {
  const location = useLocation()
  const [fileName, setFileName] = useState<string | null>(null)
  const [previewText, setPreviewText] = useState<string | null>(null)
  const [jumpTo, setJumpTo] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const lintMutation = useLintMutation()

  useEffect(() => {
    const incoming = (location.state as { file?: File } | null)?.file
    if (incoming) void handleFile(incoming)
    // eslint-disable-next-line react-hooks/exhaustive-deps -- run once for the file handed off from the Generator workspace
  }, [location.state])

  async function handleFile(file: File) {
    setFileName(file.name)
    setJumpTo(null)
    lintMutation.mutate(file)

    try {
      const mammoth = await import('mammoth')
      const arrayBuffer = await file.arrayBuffer()
      const { value } = await mammoth.extractRawText({ arrayBuffer })
      setPreviewText(value)
    } catch {
      setPreviewText(null)
    }
  }

  const findings = lintMutation.data ?? []
  const grouped = {
    error: findings.filter((f) => f.severity === 'error'),
    warning: findings.filter((f) => f.severity === 'warning'),
    info: findings.filter((f) => f.severity === 'info'),
  }

  return (
    <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
      <Stack spacing={2} sx={{ flex: '1 1 420px', minWidth: 320 }}>
        <Typography variant="h4" component="h1">
          Linter
        </Typography>
        <Button variant="contained" onClick={() => inputRef.current?.click()} sx={{ alignSelf: 'flex-start' }}>
          Upload .docx
        </Button>
        <input
          ref={inputRef}
          type="file"
          accept=".docx"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) void handleFile(file)
          }}
        />
        {fileName && <Typography color="text.secondary">{fileName}</Typography>}

        {lintMutation.isPending && <LoadingState label="Linting…" />}
        {lintMutation.isError && <Alert severity="error">Lint request failed.</Alert>}

        {lintMutation.isSuccess && findings.length === 0 && (
          <Alert severity="success">No findings — this document passes the linter.</Alert>
        )}

        {(['error', 'warning', 'info'] as const).map(
          (severity) =>
            grouped[severity].length > 0 && (
              <Box key={severity}>
                <Typography variant="subtitle1" sx={{ textTransform: 'capitalize' }}>
                  {severity} ({grouped[severity].length})
                </Typography>
                <List dense>
                  {grouped[severity].map((finding, index) => (
                    <ListItemButton
                      key={`${severity}-${index}`}
                      onClick={() => setJumpTo(finding.location ?? null)}
                      selected={jumpTo === finding.location}
                    >
                      <Chip label={finding.rule} size="small" color={SEVERITY_COLOR[severity]} sx={{ mr: 1 }} />
                      <ListItemText primary={finding.message} secondary={finding.location} />
                    </ListItemButton>
                  ))}
                </List>
              </Box>
            ),
        )}
      </Stack>

      <Box sx={{ flex: '1 1 420px', minWidth: 320 }}>
        <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
          Document preview
        </Typography>
        {!previewText && <EmptyState message="Upload a .docx to preview its text here." />}
        {previewText && (
          <Box
            sx={{
              maxHeight: 480,
              overflow: 'auto',
              p: 2,
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              whiteSpace: 'pre-wrap',
              fontSize: '0.875rem',
            }}
          >
            {/* shortcut: shows the location string instead of scrolling/highlighting matched preview text; upgrade once /lint returns offsets into the extracted text */}
            {jumpTo && (
              <Alert severity="info" sx={{ mb: 2 }}>
                Jumped to: {jumpTo}
              </Alert>
            )}
            {previewText}
          </Box>
        )}
      </Box>
    </Box>
  )
}
