import { Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Layout from './components/Layout'
import MediaLibrary from './pages/MediaLibrary'
import Transcriptions from './pages/Transcriptions'
import Processing from './pages/Processing'
import Personas from './pages/Personas'
import Templates from './pages/Templates'
import Benchmark from './pages/Benchmark'
import Settings from './pages/Settings'

function App() {
  console.log('App component rendering...')
  
  return (
    <Layout>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<Navigate to="/media" replace />} />
          <Route path="/media" element={<MediaLibrary />} />
          <Route path="/transcriptions" element={<Transcriptions />} />
          <Route path="/process" element={<Processing />} />
          <Route path="/personas" element={<Personas />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/benchmark" element={<Benchmark />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </AnimatePresence>
    </Layout>
  )
}

export default App
