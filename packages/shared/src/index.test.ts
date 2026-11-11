import { describe, expect, it } from 'vitest'
import { formatGreeting, truncate } from './index'

describe('formatGreeting', () => {
  it('greets a named person', () => {
    expect(formatGreeting('Ada')).toBe('Hello, Ada!')
  })

  it('trims whitespace and handles blank names', () => {
    expect(formatGreeting('  Ada  ')).toBe('Hello, Ada!')
    expect(formatGreeting('   ')).toBe('Hello!')
  })
})

describe('truncate', () => {
  it('returns short values unchanged', () => {
    expect(truncate('patent', 10)).toBe('patent')
  })

  it('truncates long values with an ellipsis', () => {
    expect(truncate('near private ai', 4)).toBe('near…')
  })

  it('rejects negative lengths', () => {
    expect(() => truncate('patent', -1)).toThrow(RangeError)
  })
})
