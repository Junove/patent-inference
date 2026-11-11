import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AppProviders } from '../AppProviders.tsx'
import { LinterPage } from './LinterPage.tsx'

function renderPage() {
  return render(
    <AppProviders>
      <MemoryRouter>
        <LinterPage />
      </MemoryRouter>
    </AppProviders>,
  )
}

describe('LinterPage', () => {
  it('uploads a file and shows findings grouped by severity', async () => {
    renderPage()
    const user = userEvent.setup()

    const file = new File(['dummy content'], 'application.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    })
    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    await user.upload(input, file)

    expect(await screen.findByText('error (1)')).toBeInTheDocument()
    expect(screen.getByText('Missing a "Claims" section.')).toBeInTheDocument()
    expect(screen.getByText('warning (1)')).toBeInTheDocument()
    expect(screen.getByText('application.docx')).toBeInTheDocument()
  })
})
