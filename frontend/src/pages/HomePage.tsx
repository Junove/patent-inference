import { useQuery } from '@tanstack/react-query'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import { formatGreeting } from '@near-private-ai/shared'
import { Link as RouterLink } from 'react-router-dom'
import { apiClient } from '../api/client.ts'
import { StatusCard } from '../components/StatusCard.tsx'
import { toServiceStatus } from '../lib/status.ts'

export function HomePage() {
  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data, error } = await apiClient.GET('/health')

      if (error || !data) {
        throw new Error('Health check failed')
      }

      return data
    },
  })

  return (
    <Stack spacing={3}>
      <Typography variant="h4" component="h1">
        Ask about patents
      </Typography>
      <Typography color="text.secondary">
        {formatGreeting('researcher')} Explore the Near Private AI patent assistant.
      </Typography>
      <StatusCard status={toServiceStatus(healthQuery)} />
      <Button
        component={RouterLink}
        to="/about"
        variant="contained"
        sx={{ alignSelf: 'flex-start' }}
      >
        Learn more
      </Button>
    </Stack>
  )
}
