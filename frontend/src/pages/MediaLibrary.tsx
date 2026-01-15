import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import {
  Upload,
  Cloud,
  Video,
  Music,
  Trash2,
  Play,
  CheckSquare,
  Square,
  Wand2,
  Link,
  X,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Button, Card, Tabs, Input, Modal, EmptyState, CardSkeleton, Select } from '../components/ui'
import { mediaApi, transcriptionApi } from '../services/api'
import { useAppStore } from '../store/appStore'
import { cn, formatBytes, formatDuration, formatDate } from '../lib/utils'

type MediaType = 'mp4' | 'mp3'

export default function MediaLibrary() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<MediaType>('mp4')
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)
  const [showGDriveModal, setShowGDriveModal] = useState(false)
  const [showTranscribeModal, setShowTranscribeModal] = useState(false)
  const [gdriveLink, setGdriveLink] = useState('')
  const [transcriptionModel, setTranscriptionModel] = useState('whisper-api')

  const {
    selectedMediaIds,
    toggleMediaSelection,
    clearMediaSelection,
    selectAllMedia,
  } = useAppStore()

  // Fetch media
  const { data: mediaData, isLoading } = useQuery({
    queryKey: ['media', activeTab],
    queryFn: () => mediaApi.list({ type: activeTab }),
  })

  const media = mediaData?.data?.media || []
  const filteredMedia = media.filter((m: any) => m.file_type === activeTab)

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => mediaApi.upload(file, setUploadProgress),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media'] })
      toast.success('File uploaded successfully')
      setUploadProgress(null)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Upload failed')
      setUploadProgress(null)
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => mediaApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media'] })
      toast.success('File deleted')
    },
    onError: () => toast.error('Failed to delete file'),
  })

  // Google Drive download mutation
  const gdriveMutation = useMutation({
    mutationFn: (link: string) => mediaApi.downloadFromGDrive(link),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media'] })
      toast.success('Download started from Google Drive')
      setShowGDriveModal(false)
      setGdriveLink('')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to download from Google Drive')
    },
  })

  // Transcription mutation
  const transcribeMutation = useMutation({
    mutationFn: (data: { media_ids: number[]; model: string }) =>
      transcriptionApi.generate(data.media_ids, data.model),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['media'] })
      queryClient.invalidateQueries({ queryKey: ['transcriptions'] })
      toast.success('Transcription started successfully')
      setShowTranscribeModal(false)
      clearMediaSelection()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start transcription')
    },
  })

  // Dropzone
  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach((file) => {
      uploadMutation.mutate(file)
    })
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/mp4': ['.mp4'],
      'audio/mpeg': ['.mp3'],
      'audio/wav': ['.wav'],
      'audio/m4a': ['.m4a'],
    },
    maxSize: 500 * 1024 * 1024, // 500MB
  })

  const tabs = [
    { id: 'mp4', label: 'Videos', icon: <Video className="w-4 h-4" />, count: media.filter((m: any) => m.file_type === 'mp4').length },
    { id: 'mp3', label: 'Audio', icon: <Music className="w-4 h-4" />, count: media.filter((m: any) => m.file_type === 'mp3').length },
  ]

  const selectedInCurrentTab = selectedMediaIds.filter((id) =>
    filteredMedia.some((m: any) => m.id === id)
  )

  const allSelected = filteredMedia.length > 0 && selectedInCurrentTab.length === filteredMedia.length

  const handleSelectAll = () => {
    if (allSelected) {
      clearMediaSelection()
    } else {
      selectAllMedia(filteredMedia.map((m: any) => m.id))
    }
  }

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
          <h1 className="text-2xl font-bold text-lunar-start">Media Library</h1>
          <p className="text-lunar-end mt-1">Upload and manage your media files</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            leftIcon={<Cloud className="w-4 h-4" />}
            onClick={() => setShowGDriveModal(true)}
          >
            Google Drive
          </Button>
          <Button
            leftIcon={<Upload className="w-4 h-4" />}
            onClick={() => document.getElementById('file-upload')?.click()}
          >
            Upload
          </Button>
        </div>
      </div>

      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300',
          isDragActive
            ? 'border-celestial-start bg-celestial-start/5'
            : 'border-white/10 hover:border-white/20 hover:bg-white/5'
        )}
      >
        <input {...getInputProps()} id="file-upload" />
        <div className="flex flex-col items-center">
          <div className={cn(
            'w-14 h-14 rounded-2xl flex items-center justify-center mb-4 transition-colors',
            isDragActive ? 'bg-gradient-celestial' : 'bg-gradient-stratos'
          )}>
            <Upload className={cn('w-6 h-6', isDragActive ? 'text-eclipse-end' : 'text-lunar-end')} />
          </div>
          <p className="text-lunar-start font-medium">
            {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
          </p>
          <p className="text-lunar-end text-sm mt-1">
            or click to browse (MP4, MP3, WAV, M4A - max 500MB)
          </p>
          {uploadProgress !== null && (
            <div className="w-full max-w-xs mt-4">
              <div className="h-2 bg-eclipse-start rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-celestial"
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-sm text-lunar-end mt-1">{uploadProgress}% uploaded</p>
            </div>
          )}
        </div>
      </div>

      {/* Tabs and Actions */}
      <div className="flex items-center justify-between">
        <Tabs tabs={tabs} activeTab={activeTab} onChange={(tab) => setActiveTab(tab as MediaType)} />
        
        {selectedInCurrentTab.length > 0 && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-lunar-end">
              {selectedInCurrentTab.length} selected
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearMediaSelection}
            >
              Clear
            </Button>
            <Button
              variant="celestial"
              size="sm"
              leftIcon={<Wand2 className="w-4 h-4" />}
              onClick={() => setShowTranscribeModal(true)}
            >
              Transcribe Selected
            </Button>
            <Button
              variant="danger"
              size="sm"
              leftIcon={<Trash2 className="w-4 h-4" />}
              onClick={() => {
                selectedInCurrentTab.forEach((id) => deleteMutation.mutate(id))
                clearMediaSelection()
              }}
            >
              Delete
            </Button>
          </div>
        )}
      </div>

      {/* Select All */}
      {filteredMedia.length > 0 && (
        <button
          onClick={handleSelectAll}
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

      {/* Media Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : filteredMedia.length === 0 ? (
        <EmptyState
          icon={activeTab === 'mp4' ? Video : Music}
          title={`No ${activeTab === 'mp4' ? 'videos' : 'audio files'} yet`}
          description="Upload your first file to get started with transcription"
          action={{
            label: 'Upload File',
            onClick: () => document.getElementById('file-upload')?.click(),
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {filteredMedia.map((file: any, index: number) => (
              <motion.div
                key={file.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card
                  className={cn(
                    'relative group',
                    selectedMediaIds.includes(file.id) && 'ring-2 ring-celestial-start'
                  )}
                  onClick={() => toggleMediaSelection(file.id)}
                >
                  {/* Selection checkbox */}
                  <div className="absolute top-3 left-3 z-10">
                    {selectedMediaIds.includes(file.id) ? (
                      <CheckSquare className="w-5 h-5 text-celestial-start" />
                    ) : (
                      <Square className="w-5 h-5 text-lunar-end opacity-0 group-hover:opacity-100 transition-opacity" />
                    )}
                  </div>

                  {/* Delete button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteMutation.mutate(file.id)
                    }}
                    className="absolute top-3 right-3 z-10 p-1.5 rounded-lg bg-red-600/80 text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>

                  <div className="flex items-start gap-3">
                    <div className={cn(
                      'w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0',
                      activeTab === 'mp4' ? 'bg-gradient-solar' : 'bg-gradient-celestial'
                    )}>
                      {activeTab === 'mp4' ? (
                        <Video className="w-6 h-6 text-white" />
                      ) : (
                        <Music className="w-6 h-6 text-eclipse-end" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-lunar-start truncate">
                        {file.original_filename}
                      </h3>
                      <p className="text-sm text-lunar-end mt-0.5">
                        {file.file_size ? formatBytes(file.file_size) : 'Unknown size'}
                        {file.duration && ` • ${formatDuration(file.duration)}`}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-4 pt-3 border-t border-white/5">
                    <span className="text-xs text-lunar-end">
                      {formatDate(file.created_at)}
                    </span>
                    <span className={cn(
                      'text-xs px-2 py-0.5 rounded-full',
                      file.source === 'upload' ? 'bg-white/5 text-lunar-end' :
                      file.source === 'gdrive' ? 'bg-celestial-start/20 text-celestial-start' :
                      'bg-solar-start/20 text-solar-start'
                    )}>
                      {file.source === 'gdrive' ? 'Google Drive' : file.source}
                    </span>
                  </div>

                  {file.is_processed && (
                    <div className="absolute bottom-3 right-3">
                      <div className="w-2 h-2 rounded-full bg-celestial-start" title="Transcribed" />
                    </div>
                  )}
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Google Drive Modal */}
      <Modal
        isOpen={showGDriveModal}
        onClose={() => setShowGDriveModal(false)}
        title="Download from Google Drive"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-lunar-end text-sm">
            Share your Google Drive file with the service account email, then paste the shareable link below.
          </p>
          <Input
            label="Shareable Link"
            placeholder="https://drive.google.com/file/d/..."
            value={gdriveLink}
            onChange={(e) => setGdriveLink(e.target.value)}
            leftIcon={<Link className="w-4 h-4" />}
          />
          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={() => setShowGDriveModal(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => gdriveMutation.mutate(gdriveLink)}
              loading={gdriveMutation.isPending}
              disabled={!gdriveLink}
            >
              Download
            </Button>
          </div>
        </div>
      </Modal>

      {/* Transcription Modal */}
      <Modal
        isOpen={showTranscribeModal}
        onClose={() => setShowTranscribeModal(false)}
        title="Transcribe Media Files"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-lunar-end text-sm">
            Selected {selectedInCurrentTab.length} file{selectedInCurrentTab.length !== 1 ? 's' : ''} for transcription.
          </p>
          <Select
            label="Transcription Model"
            value={transcriptionModel}
            onChange={(e) => setTranscriptionModel(e.target.value)}
            options={[
              { value: 'whisper-local', label: 'Whisper (Local)' },
              { value: 'whisper-api', label: 'Whisper API (OpenAI)' },
              { value: 'google-stt', label: 'Google Speech-to-Text' },
            ]}
          />
          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={() => setShowTranscribeModal(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => transcribeMutation.mutate({ 
                media_ids: selectedMediaIds, 
                model: transcriptionModel 
              })}
              loading={transcribeMutation.isPending}
              disabled={selectedMediaIds.length === 0}
            >
              Start Transcription
            </Button>
          </div>
        </div>
      </Modal>
    </motion.div>
  )
}
