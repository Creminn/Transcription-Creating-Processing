import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileText,
  Clipboard,
  Trash2,
  CheckSquare,
  Square,
  Search,
  Wand2,
  Clock,
  Music,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Button, Card, Tabs, Input, Textarea, Modal, EmptyState, CardSkeleton } from '../components/ui'
import { transcriptionApi } from '../services/api'
import { useAppStore } from '../store/appStore'
import { cn, formatDate, truncateText } from '../lib/utils'

export default function Transcriptions() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'all' | 'paste'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showPasteModal, setShowPasteModal] = useState(false)
  const [pasteData, setPasteData] = useState({ title: '', content: '' })
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const {
    selectedTranscriptionIds,
    toggleTranscriptionSelection,
    clearTranscriptionSelection,
    selectAllTranscriptions,
  } = useAppStore()

  // Fetch transcriptions
  const { data: transcriptionData, isLoading } = useQuery({
    queryKey: ['transcriptions'],
    queryFn: () => transcriptionApi.list(),
  })

  const transcriptions = transcriptionData?.data?.transcriptions || []
  const filteredTranscriptions = transcriptions.filter((t: any) => {
    const matchesSearch = t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesTab = activeTab === 'all' || (activeTab === 'paste' && t.source_type === 'pasted')
    return matchesSearch && matchesTab
  })

  // Paste mutation
  const pasteMutation = useMutation({
    mutationFn: (data: { title: string; content: string }) =>
      transcriptionApi.paste(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transcriptions'] })
      toast.success('Transcription saved')
      setShowPasteModal(false)
      setPasteData({ title: '', content: '' })
    },
    onError: () => toast.error('Failed to save transcription'),
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => transcriptionApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transcriptions'] })
      toast.success('Transcription deleted')
    },
    onError: () => toast.error('Failed to delete'),
  })

  const tabs = [
    { id: 'all', label: 'All', count: transcriptions.length },
    { id: 'paste', label: 'Pasted', count: transcriptions.filter((t: any) => t.source_type === 'pasted').length },
  ]

  const allSelected = filteredTranscriptions.length > 0 &&
    selectedTranscriptionIds.length === filteredTranscriptions.length

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-lunar-start">Transcriptions</h1>
          <p className="text-lunar-end mt-1">View and manage your transcriptions</p>
        </div>
        <Button
          leftIcon={<Clipboard className="w-4 h-4" />}
          onClick={() => setShowPasteModal(true)}
        >
          Paste Transcription
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="flex-1 max-w-md">
          <Input
            placeholder="Search transcriptions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={<Search className="w-4 h-4" />}
          />
        </div>
        <Tabs
          tabs={tabs}
          activeTab={activeTab}
          onChange={(tab) => setActiveTab(tab as 'all' | 'paste')}
        />
      </div>

      {/* Selection Actions */}
      {selectedTranscriptionIds.length > 0 && (
        <div className="flex items-center gap-3 p-3 bg-eclipse-start rounded-xl border border-white/5">
          <span className="text-sm text-lunar-end">
            {selectedTranscriptionIds.length} selected
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={clearTranscriptionSelection}
          >
            Clear
          </Button>
          <Button
            variant="celestial"
            size="sm"
            leftIcon={<Wand2 className="w-4 h-4" />}
          >
            Process Selected
          </Button>
          <Button
            variant="danger"
            size="sm"
            leftIcon={<Trash2 className="w-4 h-4" />}
            onClick={() => {
              selectedTranscriptionIds.forEach((id) => deleteMutation.mutate(id))
              clearTranscriptionSelection()
            }}
          >
            Delete
          </Button>
        </div>
      )}

      {/* Select All */}
      {filteredTranscriptions.length > 0 && (
        <button
          onClick={() => {
            if (allSelected) {
              clearTranscriptionSelection()
            } else {
              selectAllTranscriptions(filteredTranscriptions.map((t: any) => t.id))
            }
          }}
          className="flex items-center gap-2 text-sm text-lunar-end hover:text-lunar-start transition-colors"
        >
          {allSelected ? (
            <CheckSquare className="w-4 h-4 text-celestial-start" />
          ) : (
            <Square className="w-4 h-4" />
          )}
          Select all
        </button>
      )}

      {/* Transcription List */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : filteredTranscriptions.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No transcriptions yet"
          description={searchQuery ? 'No results found for your search' : 'Generate transcriptions from your media files or paste one directly'}
          action={!searchQuery ? {
            label: 'Paste Transcription',
            onClick: () => setShowPasteModal(true),
          } : undefined}
        />
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {filteredTranscriptions.map((transcription: any, index: number) => (
              <motion.div
                key={transcription.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ delay: index * 0.03 }}
              >
                <Card
                  className={cn(
                    'relative group',
                    selectedTranscriptionIds.includes(transcription.id) && 'ring-2 ring-celestial-start'
                  )}
                  onClick={() => toggleTranscriptionSelection(transcription.id)}
                >
                  <div className="flex items-start gap-4">
                    {/* Checkbox */}
                    <div className="pt-1">
                      {selectedTranscriptionIds.includes(transcription.id) ? (
                        <CheckSquare className="w-5 h-5 text-celestial-start" />
                      ) : (
                        <Square className="w-5 h-5 text-lunar-end opacity-0 group-hover:opacity-100 transition-opacity" />
                      )}
                    </div>

                    {/* Icon */}
                    <div className={cn(
                      'w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0',
                      transcription.source_type === 'pasted' ? 'bg-gradient-cosmic' : 'bg-gradient-celestial'
                    )}>
                      {transcription.source_type === 'pasted' ? (
                        <Clipboard className="w-5 h-5 text-eclipse-end" />
                      ) : (
                        <Music className="w-5 h-5 text-eclipse-end" />
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <h3 className="font-medium text-lunar-start">
                            {transcription.title}
                          </h3>
                          <p className="text-sm text-lunar-end mt-1 line-clamp-2">
                            {truncateText(transcription.content, 200)}
                          </p>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              setSelectedId(transcription.id)
                            }}
                            className="p-2 rounded-lg hover:bg-white/5 text-lunar-end hover:text-lunar-start transition-colors"
                          >
                            <FileText className="w-4 h-4" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              deleteMutation.mutate(transcription.id)
                            }}
                            className="p-2 rounded-lg hover:bg-red-600/20 text-lunar-end hover:text-red-500 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {/* Meta */}
                      <div className="flex items-center gap-4 mt-3 text-xs text-lunar-end">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(transcription.created_at)}
                        </span>
                        {transcription.model_used && (
                          <span className="px-2 py-0.5 rounded-full bg-celestial-start/20 text-celestial-start">
                            {transcription.model_used}
                          </span>
                        )}
                        {transcription.word_count && (
                          <span>{transcription.word_count} words</span>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Paste Modal */}
      <Modal
        isOpen={showPasteModal}
        onClose={() => setShowPasteModal(false)}
        title="Paste Transcription"
        size="lg"
      >
        <div className="space-y-4">
          <Input
            label="Title"
            placeholder="Meeting transcription - Jan 2026"
            value={pasteData.title}
            onChange={(e) => setPasteData({ ...pasteData, title: e.target.value })}
          />
          <Textarea
            label="Transcription Content"
            placeholder="Paste your transcription text here..."
            rows={12}
            value={pasteData.content}
            onChange={(e) => setPasteData({ ...pasteData, content: e.target.value })}
          />
          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={() => setShowPasteModal(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => pasteMutation.mutate(pasteData)}
              loading={pasteMutation.isPending}
              disabled={!pasteData.title || !pasteData.content}
            >
              Save Transcription
            </Button>
          </div>
        </div>
      </Modal>

      {/* View Transcription Modal */}
      <Modal
        isOpen={selectedId !== null}
        onClose={() => setSelectedId(null)}
        title={transcriptions.find((t: any) => t.id === selectedId)?.title || 'Transcription'}
        size="xl"
      >
        <div className="max-h-[60vh] overflow-y-auto">
          <pre className="text-sm text-lunar-start whitespace-pre-wrap font-sans">
            {transcriptions.find((t: any) => t.id === selectedId)?.content}
          </pre>
        </div>
      </Modal>
    </motion.div>
  )
}
