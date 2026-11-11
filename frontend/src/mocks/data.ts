import type { components } from '../api/schema'

type Patent = components['schemas']['PatentDetail']
type Project = components['schemas']['ProjectOut']
type FileOut = components['schemas']['FileOut']
type JobStatusValue = components['schemas']['JobStatus']['status']

export const patents: Patent[] = [
  {
    id: 'US-0001',
    title: 'Battery pack thermal regulation via phase-change layers',
    abstract: 'A battery pack with interleaved phase-change material layers that absorb heat during fast charging.',
    assignee: 'Volta Systems Inc.',
    filing_date: '2021-03-14',
    claims: ['A battery pack comprising a cell stack and a phase-change layer interleaved between cells.'],
    inventors: ['J. Alvarez', 'M. Chen'],
    classification: ['H01M 10/60'],
    cited_patents: [],
  },
  {
    id: 'US-0002',
    title: 'Distributed rate limiting using sliding token windows',
    abstract: 'A method for rate limiting requests across distributed nodes using a sliding token window synchronized by a gossip protocol.',
    assignee: 'Northbridge Cloud LLC',
    filing_date: '2022-07-02',
    claims: ['A method comprising maintaining a sliding token window at each of a plurality of nodes.'],
    inventors: ['R. Okafor'],
    classification: ['H04L 47/10'],
    cited_patents: [
      {
        id: 'US-0001',
        title: 'Battery pack thermal regulation via phase-change layers',
        abstract: 'A battery pack with interleaved phase-change material layers.',
      },
    ],
  },
  {
    id: 'US-0003',
    title: 'Vision-guided robotic gripper with compliant fingertips',
    abstract: 'A robotic gripper that uses a vision model to estimate grasp pose and compliant fingertips to absorb placement error.',
    assignee: 'Ferrous Robotics',
    filing_date: '2023-01-19',
    claims: ['A robotic gripper comprising a camera, a controller, and a pair of compliant fingertips.'],
    inventors: ['S. Mbeki', 'T. Lindqvist'],
    classification: ['B25J 15/08'],
    cited_patents: [],
  },
]

const initialProjects: Project[] = [
  {
    id: 'proj-1',
    name: 'Phase-change battery pack',
    description: 'Draft application covering the thermal regulation layer design.',
    created_at: '2026-11-01T09:00:00Z',
  },
]

export const projects: Project[] = [...initialProjects]
export const filesByProject = new Map<string, FileOut[]>([['proj-1', []]])
export const jobs = new Map<string, { status: JobStatusValue; project_id: string; sections: string[] }>()
// Mirrors the real backend's next_version(): max version so far for a project, plus one.
export const documentVersions = new Map<string, number>()

let nextId = 100
export function newId(prefix: string): string {
  nextId += 1
  return `${prefix}-${nextId}`
}

export function nextDocumentVersion(projectId: string): number {
  const version = (documentVersions.get(projectId) ?? 0) + 1
  documentVersions.set(projectId, version)
  return version
}

/** Restores the mock store to its initial fixture state; call between test cases. */
export function resetMockData() {
  projects.length = 0
  projects.push(...initialProjects.map((p) => ({ ...p })))
  filesByProject.clear()
  filesByProject.set('proj-1', [])
  jobs.clear()
  documentVersions.clear()
  nextId = 100
}
