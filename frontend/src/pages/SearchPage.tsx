import { useState } from 'react'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Card from '@mui/material/Card'
import CardActionArea from '@mui/material/CardActionArea'
import CardContent from '@mui/material/CardContent'
import Chip from '@mui/material/Chip'
import Stack from '@mui/material/Stack'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { emptyFilters, PAGE_SIZE, usePatentQuery, useSearchQuery, type SearchFilters } from '../api/search.ts'
import { EmptyState, ErrorState, LoadingState } from '../components/StateViews.tsx'

export function SearchPage() {
  const [filters, setFilters] = useState<SearchFilters>(emptyFilters)
  const [submitted, setSubmitted] = useState<SearchFilters>(emptyFilters)
  const [page, setPage] = useState(1)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const searchQuery = useSearchQuery(submitted, page, true)
  const patentQuery = usePatentQuery(selectedId)

  function handleSearch() {
    setPage(1)
    setSubmitted(filters)
  }

  return (
    <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
      <Stack spacing={2} sx={{ flex: '1 1 420px', minWidth: 320 }}>
        <Typography variant="h4" component="h1">
          Patent search
        </Typography>
        <TextField
          label="Keyword"
          value={filters.q}
          onChange={(e) => setFilters({ ...filters, q: e.target.value })}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <Stack direction="row" spacing={2}>
          <TextField
            label="Date from"
            type="date"
            value={filters.dateFrom}
            onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
            slotProps={{ inputLabel: { shrink: true } }}
            fullWidth
          />
          <TextField
            label="Date to"
            type="date"
            value={filters.dateTo}
            onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
            slotProps={{ inputLabel: { shrink: true } }}
            fullWidth
          />
        </Stack>
        <TextField
          label="Assignee"
          value={filters.assignee}
          onChange={(e) => setFilters({ ...filters, assignee: e.target.value })}
        />
        <TextField
          label="Inventor"
          value={filters.inventor}
          onChange={(e) => setFilters({ ...filters, inventor: e.target.value })}
        />
        <TextField
          label="Classification code"
          value={filters.classification}
          onChange={(e) => setFilters({ ...filters, classification: e.target.value })}
        />
        <Button variant="contained" onClick={handleSearch} sx={{ alignSelf: 'flex-start' }}>
          Search
        </Button>

        {searchQuery.isPending && <LoadingState label="Searching…" />}
        {searchQuery.isError && <ErrorState message="Search failed. Check the backend connection." />}
        {searchQuery.data && searchQuery.data.results.length === 0 && (
          <EmptyState message="No patents match these filters." />
        )}
        {searchQuery.data && searchQuery.data.results.length > 0 && (
          <Stack spacing={1}>
            <Typography variant="body2" color="text.secondary">
              {searchQuery.data.total} result{searchQuery.data.total === 1 ? '' : 's'}
            </Typography>
            {searchQuery.data.results.map((patent) => (
              <Card key={patent.id} variant={selectedId === patent.id ? 'elevation' : 'outlined'}>
                <CardActionArea onClick={() => setSelectedId(patent.id)}>
                  <CardContent>
                    <Typography variant="subtitle1">{patent.title}</Typography>
                    <Typography variant="body2" color="text.secondary" noWrap>
                      {patent.assignee ?? 'Unknown assignee'} · {patent.filing_date ?? 'no filing date'}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            ))}
            <Stack direction="row" spacing={2} sx={{ alignItems: 'center', alignSelf: 'center' }}>
              <Button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                Previous
              </Button>
              <Typography variant="body2">Page {page}</Typography>
              <Button
                disabled={(page - 1) * PAGE_SIZE + searchQuery.data.results.length >= searchQuery.data.total}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </Stack>
          </Stack>
        )}
      </Stack>

      <Box sx={{ flex: '1 1 420px', minWidth: 320 }}>
        <Typography variant="h5" component="h2" sx={{ mb: 2 }}>
          Details
        </Typography>
        {!selectedId && <EmptyState message="Select a result to see its full record." />}
        {selectedId && patentQuery.isPending && <LoadingState label="Loading patent…" />}
        {selectedId && patentQuery.isError && <ErrorState message="Failed to load this patent." />}
        {patentQuery.data && (
          <Stack spacing={2}>
            <Typography variant="h6">{patentQuery.data.title}</Typography>
            <Typography color="text.secondary">{patentQuery.data.abstract}</Typography>
            <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
              {patentQuery.data.classification.map((code) => (
                <Chip key={code} label={code} size="small" />
              ))}
            </Stack>
            <Typography variant="body2">
              Inventors: {patentQuery.data.inventors.join(', ') || 'none listed'}
            </Typography>
            <Typography variant="subtitle2">Claims</Typography>
            <Stack component="ol" spacing={1} sx={{ pl: 3 }}>
              {patentQuery.data.claims.map((claim, index) => (
                <Typography component="li" key={index} variant="body2">
                  {claim}
                </Typography>
              ))}
            </Stack>
            {patentQuery.data.cited_patents.length > 0 && (
              <>
                <Typography variant="subtitle2">Cited patents</Typography>
                <Stack spacing={1}>
                  {patentQuery.data.cited_patents.map((cited) => (
                    <Typography key={cited.id} variant="body2">
                      {cited.id} — {cited.title}
                    </Typography>
                  ))}
                </Stack>
              </>
            )}
          </Stack>
        )}
      </Box>
    </Box>
  )
}
