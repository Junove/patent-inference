import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterAll, afterEach } from 'vitest'
import { resetMockData } from '../mocks/data.ts'
import { server } from '../mocks/server.ts'

// Started at the top level (not inside beforeAll) so MSW patches globalThis.fetch
// before api/client.ts's `createClient()` call captures it as its default fetch impl.
server.listen({ onUnhandledRequest: 'error' })

afterEach(() => {
  cleanup()
  server.resetHandlers()
  resetMockData()
})

afterAll(() => server.close())
