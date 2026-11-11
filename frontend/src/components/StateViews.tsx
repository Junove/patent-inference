import Alert from '@mui/material/Alert'
import CircularProgress from '@mui/material/CircularProgress'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <Stack direction="row" spacing={2} sx={{ py: 4, alignItems: 'center' }}>
      <CircularProgress size={24} />
      <Typography color="text.secondary">{label}</Typography>
    </Stack>
  )
}

export function ErrorState({ message }: { message: string }) {
  return <Alert severity="error">{message}</Alert>
}

export function EmptyState({ message }: { message: string }) {
  return (
    <Typography color="text.secondary" sx={{ py: 4 }}>
      {message}
    </Typography>
  )
}
