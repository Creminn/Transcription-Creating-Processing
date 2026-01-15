import { create } from 'zustand'

interface Media {
  id: number
  filename: string
  original_filename: string
  filepath: string
  file_type: 'mp4' | 'mp3' | 'wav' | 'm4a'
  source: 'upload' | 'gdrive' | 'converted'
  file_size: number | null
  duration: number | null
  is_processed: boolean
  created_at: string
}

interface Transcription {
  id: number
  media_id: number | null
  title: string
  content: string
  model_used: string | null
  source_type: 'model' | 'pasted'
  word_count: number | null
  created_at: string
}

interface AppState {
  // Selected items
  selectedMediaIds: number[]
  selectedTranscriptionIds: number[]
  
  // UI state
  sidebarCollapsed: boolean
  
  // Actions
  toggleMediaSelection: (id: number) => void
  clearMediaSelection: () => void
  selectAllMedia: (ids: number[]) => void
  
  toggleTranscriptionSelection: (id: number) => void
  clearTranscriptionSelection: () => void
  selectAllTranscriptions: (ids: number[]) => void
  
  toggleSidebar: () => void
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  selectedMediaIds: [],
  selectedTranscriptionIds: [],
  sidebarCollapsed: false,
  
  // Media selection actions
  toggleMediaSelection: (id) =>
    set((state) => ({
      selectedMediaIds: state.selectedMediaIds.includes(id)
        ? state.selectedMediaIds.filter((i) => i !== id)
        : [...state.selectedMediaIds, id],
    })),
  
  clearMediaSelection: () => set({ selectedMediaIds: [] }),
  
  selectAllMedia: (ids) => set({ selectedMediaIds: ids }),
  
  // Transcription selection actions
  toggleTranscriptionSelection: (id) =>
    set((state) => ({
      selectedTranscriptionIds: state.selectedTranscriptionIds.includes(id)
        ? state.selectedTranscriptionIds.filter((i) => i !== id)
        : [...state.selectedTranscriptionIds, id],
    })),
  
  clearTranscriptionSelection: () => set({ selectedTranscriptionIds: [] }),
  
  selectAllTranscriptions: (ids) => set({ selectedTranscriptionIds: ids }),
  
  // UI actions
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
}))
