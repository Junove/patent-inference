import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Typography from '@mui/material/Typography'

export type ServiceStatus = 'loading' | 'ok' | 'error'

const STATUS_LABELS: Record<ServiceStatus, string> = {
  loading: 'Checking service…',
  ok: 'Service online',
  error: 'Service unavailable',
}

interface StatusCardProps {
  status: ServiceStatus
}

export function StatusCard({ status }: StatusCardProps) {
  return (
    <Card variant="outlined" data-testid="status-card">
      <CardContent>
        <Typography variant="overline" color="text.secondary">
          API status
        </Typography>
        <Typography variant="h5" component="p">
          {STATUS_LABELS[status]}
        </Typography>
      </CardContent>
    </Card>
  )
}
