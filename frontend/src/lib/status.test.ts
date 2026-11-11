import { describe, expect, it } from 'vitest'
import { toServiceStatus } from './status.ts'

describe('toServiceStatus', () => {
  it('maps a pending query to loading', () => {
    expect(toServiceStatus({ isPending: true, isError: false })).toBe('loading')
  })

  it('maps a failed query to error', () => {
    expect(toServiceStatus({ isPending: false, isError: true })).toBe('error')
  })

  it('maps a successful query to ok', () => {
    expect(toServiceStatus({ isPending: false, isError: false })).toBe('ok')
  })
})
