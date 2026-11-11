import { http, HttpResponse } from 'msw'
import { filesByProject, jobs, newId, nextDocumentVersion, patents, projects } from './data'
import type { components } from '../api/schema'

type Finding = components['schemas']['Finding']
type ApiError = components['schemas']['Error']

const SECTION_NAMES = ['title', 'abstract', 'background', 'summary', 'claims']

// Wildcard origin: matches regardless of the configured backend URL (and, importantly,
// avoids importing api/client.ts here — that would create apiClient's fetch client, which
// captures `fetch` as a default param, before MSW gets a chance to patch it in tests).
const api = (path: string) => `*/api/v1${path}`

function notFound(message: string) {
  return HttpResponse.json<ApiError>({ code: 'not_found', message }, { status: 404 })
}

export const handlers = [
  http.get(api('/health'), () => HttpResponse.json({ status: 'ok', version: 'mock' })),

  http.get(api('/projects'), () => HttpResponse.json(projects)),

  http.post(api('/projects'), async ({ request }) => {
    const body = (await request.json()) as { name: string; description?: string }
    const project = {
      id: newId('proj'),
      name: body.name,
      description: body.description ?? '',
      created_at: new Date().toISOString(),
    }
    projects.push(project)
    filesByProject.set(project.id, [])
    return HttpResponse.json(project, { status: 201 })
  }),

  http.get(api('/patents/search'), ({ request }) => {
    const url = new URL(request.url)
    const q = (url.searchParams.get('q') ?? '').toLowerCase()
    const assignee = url.searchParams.get('assignee')?.toLowerCase()
    const inventor = url.searchParams.get('inventor')?.toLowerCase()
    const classification = url.searchParams.get('classification')?.toLowerCase()

    const results = patents.filter((p) => {
      if (q && !`${p.title} ${p.abstract}`.toLowerCase().includes(q)) return false
      if (assignee && !p.assignee?.toLowerCase().includes(assignee)) return false
      if (inventor && !p.inventors.some((i) => i.toLowerCase().includes(inventor))) return false
      if (classification && !p.classification.some((c) => c.toLowerCase().includes(classification))) return false
      return true
    })

    return HttpResponse.json({
      results: results.map(({ id, title, abstract, assignee: a, filing_date }) => ({
        id,
        title,
        abstract,
        assignee: a,
        filing_date,
      })),
      total: results.length,
    })
  }),

  http.get(api('/patents/:patentId'), ({ params }) => {
    const patent = patents.find((p) => p.id === params.patentId)
    return patent ? HttpResponse.json(patent) : notFound(`Patent ${params.patentId as string} not found`)
  }),

  http.post(api('/lint'), async () => {
    const findings: Finding[] = [
      { severity: 'error', rule: 'FR-L2', message: 'Missing a "Claims" section.', location: 'end of document' },
      { severity: 'warning', rule: 'FR-L4', message: 'Abstract exceeds 150 words.', location: 'Abstract' },
      { severity: 'info', rule: 'FR-L3', message: 'Claim 4 is dependent on claim 3.', location: 'Claims ¶4' },
    ]
    return HttpResponse.json(findings)
  }),

  http.get(api('/projects/:projectId/files'), ({ params }) => {
    const files = filesByProject.get(params.projectId as string)
    return files ? HttpResponse.json(files) : notFound(`Project ${params.projectId as string} not found`)
  }),

  http.post(api('/projects/:projectId/files'), async ({ params, request }) => {
    const projectId = params.projectId as string
    const files = filesByProject.get(projectId)
    if (!files) return notFound(`Project ${projectId} not found`)

    const form = await request.formData()
    const file = form.get('file') as File | null
    const record = {
      id: newId('file'),
      filename: file?.name ?? 'upload.bin',
      content_type: file?.type ?? 'application/octet-stream',
      size: file?.size ?? 0,
      created_at: new Date().toISOString(),
    }
    files.push(record)
    return HttpResponse.json(record, { status: 201 })
  }),

  http.delete(api('/projects/:projectId/files/:fileId'), ({ params }) => {
    const files = filesByProject.get(params.projectId as string)
    if (!files) return notFound(`Project ${params.projectId as string} not found`)
    const index = files.findIndex((f) => f.id === params.fileId)
    if (index === -1) return notFound(`File ${params.fileId as string} not found`)
    files.splice(index, 1)
    return new HttpResponse(null, { status: 204 })
  }),

  http.post(api('/projects/:projectId/generate'), ({ params }) => {
    const jobId = newId('job')
    jobs.set(jobId, { status: 'queued', project_id: params.projectId as string, sections: [...SECTION_NAMES] })
    return HttpResponse.json({ job_id: jobId }, { status: 202 })
  }),

  http.post(api('/projects/:projectId/sections/:name/regenerate'), ({ params }) => {
    const jobId = newId('job')
    jobs.set(jobId, {
      status: 'queued',
      project_id: params.projectId as string,
      sections: [params.name as string],
    })
    return HttpResponse.json({ job_id: jobId }, { status: 202 })
  }),

  http.post(api('/jobs/:jobId/cancel'), ({ params }) => {
    const job = jobs.get(params.jobId as string)
    if (!job) return notFound(`Job ${params.jobId as string} not found`)
    job.status = 'cancelled'
    return HttpResponse.json({ job_id: params.jobId, status: job.status })
  }),

  // Mocks the SSE stream the real backend serves while a generation job runs, matching
  // app/generator/runner.py's `_sse` format exactly: a named `event:` line (status/section/
  // token) plus `data:`, with section text arriving as per-section token deltas rather than
  // on the `section` event itself.
  http.get(api('/jobs/:jobId/events'), ({ params }) => {
    const jobId = params.jobId as string
    const job = jobs.get(jobId)
    if (!job) return notFound(`Job ${jobId} not found`)

    const encoder = new TextEncoder()
    const send = (controller: ReadableStreamDefaultController<Uint8Array>, event: string, data: Record<string, unknown>) =>
      controller.enqueue(encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`))

    const stream = new ReadableStream<Uint8Array>({
      async start(controller) {
        job.status = 'running'
        send(controller, 'status', { job_id: jobId, status: 'running' })

        for (const name of job.sections) {
          send(controller, 'section', { name, status: 'running' })
          for (const word of `Mock draft text for "${name}".`.split(' ')) {
            await new Promise((resolve) => setTimeout(resolve, 60))
            send(controller, 'token', { name, delta: `${word} ` })
          }
          send(controller, 'section', { name, status: 'done' })
        }

        job.status = 'succeeded'
        const version = nextDocumentVersion(job.project_id)
        send(controller, 'status', { job_id: jobId, status: 'succeeded', version })
        controller.close()
      },
    })

    return new HttpResponse(stream, {
      headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' },
    })
  }),

  http.get(api('/projects/:projectId/documents/:version'), () =>
    new HttpResponse(new Blob(['mock docx content']), {
      headers: {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      },
    }),
  ),
]
