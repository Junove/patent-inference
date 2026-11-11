import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { AppProviders } from '../AppProviders.tsx'
import { SearchPage } from './SearchPage.tsx'

function renderPage() {
  return render(
    <AppProviders>
      <SearchPage />
    </AppProviders>,
  )
}

describe('SearchPage', () => {
  it('searches and loads the selected result detail', async () => {
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText('Keyword'), 'battery')
    await user.click(screen.getByRole('button', { name: 'Search' }))

    const result = await screen.findByText('Battery pack thermal regulation via phase-change layers')
    await user.click(result)

    await waitFor(() =>
      expect(
        screen.getByText(
          'A battery pack with interleaved phase-change material layers that absorb heat during fast charging.',
        ),
      ).toBeInTheDocument(),
    )
  })

  it('shows an empty state when nothing matches', async () => {
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText('Keyword'), 'nonexistent-term-xyz')
    await user.click(screen.getByRole('button', { name: 'Search' }))

    expect(await screen.findByText('No patents match these filters.')).toBeInTheDocument()
  })
})
