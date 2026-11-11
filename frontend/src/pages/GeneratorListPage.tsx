import { useState } from 'react'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardActionArea from '@mui/material/CardActionArea'
import CardContent from '@mui/material/CardContent'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogTitle from '@mui/material/DialogTitle'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { useNavigate } from 'react-router-dom'
import { useCreateProjectMutation, useProjectsQuery } from '../api/projects.ts'
import { EmptyState, ErrorState, LoadingState } from '../components/StateViews.tsx'

export function GeneratorListPage() {
  const navigate = useNavigate()
  const projectsQuery = useProjectsQuery()
  const createProject = useCreateProjectMutation()
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  async function handleCreate() {
    const project = await createProject.mutateAsync({ name, description })
    setOpen(false)
    setName('')
    setDescription('')
    navigate(`/generator/${project.id}`)
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Generator projects
        </Typography>
        <Button variant="contained" onClick={() => setOpen(true)}>
          New project
        </Button>
      </Stack>

      {projectsQuery.isPending && <LoadingState label="Loading projects…" />}
      {projectsQuery.isError && <ErrorState message="Failed to load projects." />}
      {projectsQuery.data?.length === 0 && (
        <EmptyState message="No projects yet — create one to start drafting a patent." />
      )}

      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        {projectsQuery.data?.map((project) => (
          <Card key={project.id} sx={{ width: 320 }}>
            <CardActionArea onClick={() => navigate(`/generator/${project.id}`)}>
              <CardContent>
                <Typography variant="subtitle1">{project.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {project.description || 'No description'}
                </Typography>
              </CardContent>
            </CardActionArea>
          </Card>
        ))}
      </Box>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth>
        <DialogTitle>New project</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <TextField label="Name" value={name} onChange={(e) => setName(e.target.value)} autoFocus fullWidth />
            <TextField
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              fullWidth
              multiline
              minRows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled={!name || createProject.isPending} onClick={handleCreate}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}
