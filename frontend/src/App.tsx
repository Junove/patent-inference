import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/AppLayout.tsx'
import { GeneratorListPage } from './pages/GeneratorListPage.tsx'
import { GeneratorProjectPage } from './pages/GeneratorProjectPage.tsx'
import { LinterPage } from './pages/LinterPage.tsx'
import { SearchPage } from './pages/SearchPage.tsx'
import { SettingsPage } from './pages/SettingsPage.tsx'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/search" replace />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="linter" element={<LinterPage />} />
        <Route path="generator" element={<GeneratorListPage />} />
        <Route path="generator/:projectId" element={<GeneratorProjectPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}
