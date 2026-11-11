/**
 * Small, framework-agnostic helpers shared by the frontend and other packages.
 */

export function formatGreeting(name: string): string {
  const trimmed = name.trim()
  return trimmed.length > 0 ? `Hello, ${trimmed}!` : 'Hello!'
}

export function truncate(value: string, maxLength: number): string {
  if (maxLength < 0) {
    throw new RangeError('maxLength must be greater than or equal to 0')
  }

  if (value.length <= maxLength) {
    return value
  }

  return `${value.slice(0, maxLength)}…`
}
