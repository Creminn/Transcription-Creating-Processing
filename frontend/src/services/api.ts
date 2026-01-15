import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
    if (error.response?.status === 500) {
      console.error('Server error:', error.response.data)
    }
    return Promise.reject(error)
  }
)

// Media API
export const mediaApi = {
  list: (params?: { type?: string; page?: number; limit?: number }) =>
    api.get('/media', { params }),
  get: (id: number) => api.get(`/media/${id}`),
  upload: (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/media/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          onProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total))
        }
      },
    })
  },
  downloadFromGDrive: (link: string) =>
    api.post('/media/gdrive', { link }),
  delete: (id: number) => api.delete(`/media/${id}`),
  convert: (id: number) => api.post(`/media/convert/${id}`),
}

// Transcription API
export const transcriptionApi = {
  list: (params?: { page?: number; limit?: number; source?: string }) =>
    api.get('/transcriptions', { params }),
  get: (id: number) => api.get(`/transcriptions/${id}`),
  generate: (mediaIds: number[], model: string) =>
    api.post('/transcriptions/generate', { media_ids: mediaIds, model }),
  paste: (data: { title: string; content: string }) =>
    api.post('/transcriptions/paste', data),
  delete: (id: number) => api.delete(`/transcriptions/${id}`),
}

// Processing API
export const processingApi = {
  getPromptTypes: () => api.get('/process/prompts'),
  process: (data: {
    transcription_ids: number[]
    prompt_type: string
    llm_model: string
    persona_id?: number
    template_id?: number
    custom_prompt?: string
  }) => api.post('/process', data),
  getHistory: () => api.get('/process/history'),
}

// Persona API
export const personaApi = {
  list: () => api.get('/personas'),
  get: (id: number) => api.get(`/personas/${id}`),
  create: (data: { name: string; sample_emails: string[]; style_description: string }) =>
    api.post('/personas', data),
  update: (id: number, data: { name?: string; sample_emails?: string[]; style_description?: string }) =>
    api.put(`/personas/${id}`, data),
  delete: (id: number) => api.delete(`/personas/${id}`),
}

// Template API
export const templateApi = {
  list: (category?: string) => api.get('/templates', { params: { category } }),
  get: (id: number) => api.get(`/templates/${id}`),
  create: (data: { name: string; category: string; template_content: string }) =>
    api.post('/templates', data),
  update: (id: number, data: { name?: string; category?: string; template_content?: string }) =>
    api.put(`/templates/${id}`, data),
  delete: (id: number) => api.delete(`/templates/${id}`),
}

// Benchmark API
export const benchmarkApi = {
  listResults: () => api.get('/benchmark/results'),
  getResult: (id: number) => api.get(`/benchmark/results/${id}`),
  runTranscription: (data: { media_id: number; model_a: string; model_b: string }) =>
    api.post('/benchmark/transcription', data),
  runLLM: (data: {
    transcription_id: number
    prompt_type: string
    model_a: string
    model_b: string
  }) => api.post('/benchmark/llm', data),
}

// Settings API
export const settingsApi = {
  get: () => api.get('/settings'),
  update: (data: Record<string, unknown>) => api.put('/settings', data),
  getModels: () => api.get('/settings/models'),
}
