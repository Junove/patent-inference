import { render, screen } from '@testing-library/react'
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
  it('renders the about page at /about', () => {
    renderApp('/about')

    expect(
      screen.getByRole('heading', { level: 1, name: 'About Near Private AI' }),
    ).toBeInTheDocument()
    expect(screen.getAllByText('Near Private AI').length).toBeGreaterThan(0)
  })

  it('renders the home page with the patent prompt', () => {
    renderApp('/')

    expect(
      screen.getByRole('heading', { level: 1, name: 'Ask about patents' }),
    ).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Learn more' })).toBeInTheDocument()
  })
})
