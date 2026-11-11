import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

export function AboutPage() {
  return (
    <Stack spacing={2}>
      <Typography variant="h4" component="h1">
        About Near Private AI
      </Typography>
      <Typography color="text.secondary">
        A private, contract-driven frontend for exploring patent questions.
      </Typography>
      <Typography color="text.secondary">
        The typed API client is generated from <code>contract/openapi.yaml</code>,
        unit and component tests run with Vitest, and the app uses React Router,
        TanStack Query, and MUI.
      </Typography>
    </Stack>
  )
}
