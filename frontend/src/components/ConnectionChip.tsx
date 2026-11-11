import Chip from '@mui/material/Chip'
import { useHealthQuery } from '../api/health.ts'
import { toServiceStatus } from '../lib/status.ts'

const COLOR = { loading: 'default', ok: 'success', error: 'error' } as const
const LABEL = { loading: 'Checking…', ok: 'Connected', error: 'Disconnected' } as const

export function ConnectionChip() {
  const status = toServiceStatus(useHealthQuery())
  return <Chip size="small" color={COLOR[status]} label={LABEL[status]} data-testid="connection-chip" />
}
