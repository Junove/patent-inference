import type { ServiceStatus } from '../components/StatusCard.tsx'

interface QueryState {
  isPending: boolean
  isError: boolean
}

export function toServiceStatus({ isPending, isError }: QueryState): ServiceStatus {
  if (isPending) {
    return 'loading'
  }

  return isError ? 'error' : 'ok'
}
