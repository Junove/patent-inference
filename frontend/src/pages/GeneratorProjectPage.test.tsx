import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AppProviders } from '../AppProviders.tsx'
import { GeneratorProjectPage } from './GeneratorProjectPage.tsx'

function renderPage() {
  return render(
    <AppProviders>
      <MemoryRouter initialEntries={['/generator/proj-1']}>
        <Routes>
          <Route path="/generator/:projectId" element={<GeneratorProjectPage />} />
        </Routes>
      </MemoryRouter>
    </AppProviders>,
  )
}

describe('GeneratorProjectPage', () => {
  it(
    'runs a generation job and streams section drafts to completion',
    async () => {
      renderPage()
      const user = userEvent.setup()

      expect(await screen.findByText('Phase-change battery pack')).toBeInTheDocument()

      await user.click(screen.getByRole('button', { name: 'Generate' }))

      await waitFor(() => expect(screen.getByText('succeeded')).toBeInTheDocument(), { timeout: 4000 })
      expect(screen.getByText('title')).toBeInTheDocument()
      expect(await screen.findByRole('link', { name: 'Download .docx' })).toBeInTheDocument()
    },
    10000,
  )
})
