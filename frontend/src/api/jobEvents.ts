import { useEffect, useRef, useState } from 'react'
import { API_BASE_URL } from './client.ts'
import type { components } from './schema'

export type JobStatusValue = components['schemas']['JobStatus']['status']

interface StatusEventData {
  job_id: string
  status: JobStatusValue
  error?: string
  version?: number
}

interface SectionEventData {
  name: string
  status: 'running' | 'done' | 'failed'
  error?: string
}

interface TokenEventData {
  name: string
  delta: string
}

export interface JobStreamState {
  status: JobStatusValue | 'idle'
  sections: Record<string, string>
  sectionErrors: Record<string, string>
  documentVersion: number | null
  error: string | null
}

const INITIAL_STATE: JobStreamState = {
  status: 'idle',
  sections: {},
  sectionErrors: {},
  documentVersion: null,
  error: null,
}

/**
 * Consumes the backend's SSE job stream via `fetch` + a stream reader rather than
 * `EventSource`, since EventSource requests aren't reliably intercepted by the MSW
 * mock's service worker, while `fetch` is. Frames carry a named `event:` line
 * (status/section/token, per app/generator/runner.py's `_sse` helper) alongside the
 * `data:` line -- section text itself streams in as per-section `token` deltas, not
 * on the `section` event, so it's accumulated here as deltas arrive.
 */
export function useJobStream(jobId: string | null) {
  const [state, setState] = useState<JobStreamState>(INITIAL_STATE)
  const controllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    if (!jobId) return
    setState({ ...INITIAL_STATE, status: 'queued' })

    const controller = new AbortController()
    controllerRef.current = controller

    async function run() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${jobId}/events`, {
          signal: controller.signal,
        })
        if (!response.ok || !response.body) throw new Error('Job stream request failed')

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        for (;;) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          const frames = buffer.split('\n\n')
          buffer = frames.pop() ?? ''
          for (const frame of frames) {
            const lines = frame.split('\n')
            const dataLine = lines.find((l) => l.startsWith('data: '))
            if (!dataLine) continue
            const eventName = lines.find((l) => l.startsWith('event: '))?.slice('event: '.length) ?? 'message'
            const payload = JSON.parse(dataLine.slice('data: '.length))

            setState((prev) => {
              if (eventName === 'status') {
                const data = payload as StatusEventData
                return {
                  ...prev,
                  status: data.status,
                  error: data.error ?? prev.error,
                  documentVersion: data.version ?? prev.documentVersion,
                }
              }
              if (eventName === 'section') {
                const data = payload as SectionEventData
                if (data.status === 'failed') {
                  return { ...prev, sectionErrors: { ...prev.sectionErrors, [data.name]: data.error ?? 'Failed' } }
                }
                if (data.status === 'running') {
                  // A retried attempt starts over -- drop any partial text/error from the last one.
                  const { [data.name]: _unused, ...sectionErrors } = prev.sectionErrors
                  return { ...prev, sections: { ...prev.sections, [data.name]: '' }, sectionErrors }
                }
                return prev
              }
              if (eventName === 'token') {
                const data = payload as TokenEventData
                return { ...prev, sections: { ...prev.sections, [data.name]: (prev.sections[data.name] ?? '') + data.delta } }
              }
              return prev
            })
          }
        }
      } catch (err) {
        if (controller.signal.aborted) return
        setState((prev) => ({ ...prev, error: err instanceof Error ? err.message : 'Job stream failed' }))
      }
    }

    run()
    return () => controller.abort()
  }, [jobId])

  // The mock backend keeps streaming section/status events after a cancel request,
  // so abort the in-flight read ourselves and reflect cancellation immediately.
  function cancel() {
    controllerRef.current?.abort()
    setState((prev) => ({ ...prev, status: 'cancelled' }))
  }

  return { ...state, cancel }
}
