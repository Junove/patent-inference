import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import App from './App.tsx'
import { AppProviders } from './AppProviders.tsx'

function renderApp(initialPath: string) {
  return render(
    <AppProviders>
      <MemoryRouter initialEntries={[initialPath]}>
        <App />
      </MemoryRouter>
    </AppProviders>,
  )
}

describe('App routing', () => {
  it('redirects the index route to the search workspace', async () => {
    renderApp('/')
    expect(await screen.findByRole('heading', { level: 1, name: 'Patent search' })).toBeInTheDocument()
  })

  it('navigates to the settings page from the sidebar', async () => {
    renderApp('/search')
    const user = userEvent.setup()
    await user.click(screen.getByRole('link', { name: 'Settings' }))
    expect(await screen.findByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
  })

  it('shows the connection status chip', async () => {
    renderApp('/search')
    expect(await screen.findByTestId('connection-chip')).toBeInTheDocument()
  })
})
