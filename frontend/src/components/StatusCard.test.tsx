import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { StatusCard } from './StatusCard.tsx'

describe('StatusCard', () => {
  it('shows a loading message while the service is being checked', () => {
    render(<StatusCard status="loading" />)

    expect(screen.getByTestId('status-card')).toBeInTheDocument()
    expect(screen.getByText('Checking service…')).toBeInTheDocument()
  })

  it('shows the online state', () => {
    render(<StatusCard status="ok" />)

    expect(screen.getByText('Service online')).toBeInTheDocument()
  })

  it('shows the unavailable state', () => {
    render(<StatusCard status="error" />)

    expect(screen.getByText('Service unavailable')).toBeInTheDocument()
  })
})
