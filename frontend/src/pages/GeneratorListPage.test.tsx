import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AppProviders } from '../AppProviders.tsx'
import { GeneratorListPage } from './GeneratorListPage.tsx'

function renderPage() {
  return render(
    <AppProviders>
      <MemoryRouter>
        <GeneratorListPage />
      </MemoryRouter>
    </AppProviders>,
  )
}

describe('GeneratorListPage', () => {
  it('lists the seeded project and creates a new one', async () => {
    renderPage()
    const user = userEvent.setup()

    expect(await screen.findByText('Phase-change battery pack')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'New project' }))
    await user.type(screen.getByLabelText('Name'), 'Robotic gripper draft')
    await user.click(screen.getByRole('button', { name: 'Create' }))

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })
})
