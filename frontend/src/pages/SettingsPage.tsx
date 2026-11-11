import { useState } from 'react'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { API_BASE_URL, API_BASE_URL_STORAGE_KEY } from '../api/client.ts'
import { useHealthQuery } from '../api/health.ts'
import { StatusCard } from '../components/StatusCard.tsx'
import { toServiceStatus } from '../lib/status.ts'

export function SettingsPage() {
  const [url, setUrl] = useState(API_BASE_URL)
  const health = useHealthQuery()

  function save() {
    try {
      localStorage.setItem(API_BASE_URL_STORAGE_KEY, url)
    } catch {
      // ignore storage failures (e.g. private browsing)
    }
    window.location.reload()
  }

  return (
    <Stack spacing={3} sx={{ maxWidth: 480 }}>
      <Typography variant="h4" component="h1">
        Settings
      </Typography>
      <TextField label="Backend URL" value={url} onChange={(e) => setUrl(e.target.value)} fullWidth />
      <Typography variant="body2" color="text.secondary">
        API keys live only in the backend&apos;s environment and are never entered or shown here.
      </Typography>
      <Button variant="contained" onClick={save} sx={{ alignSelf: 'flex-start' }}>
        Save and reload
      </Button>
      <StatusCard status={toServiceStatus(health)} />
      <Button onClick={() => health.refetch()} sx={{ alignSelf: 'flex-start' }}>
        Recheck connection
      </Button>
    </Stack>
  )
}
