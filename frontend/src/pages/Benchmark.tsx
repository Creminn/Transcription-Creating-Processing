import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BarChart3,
  Mic,
  Brain,
  Play,
  Trophy,
  Clock,
  FileText,
  ChevronRight,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Button, Card, Select, Tabs, EmptyState, CardSkeleton } from '../components/ui'
import { benchmarkApi, mediaApi, transcriptionApi } from '../services/api'
import { cn, formatDate } from '../lib/utils'

const transcriptionModels = [
  { value: 'whisper-large', label: 'Whisper Large (Local)' },
  { value: 'whisper-base', label: 'Whisper Base (Local)' },
  { value: 'whisper-api', label: 'Whisper API (OpenAI)' },
  { value: 'google-stt', label: 'Google Speech-to-Text' },
]

const llmModels = [
  { value: 'gpt-4', label: 'GPT-4 (OpenAI)' },
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo (OpenAI)' },
  { value: 'gemini-pro', label: 'Gemini Pro (Google)' },
  { value: 'llama2', label: 'Llama 2 (Ollama)' },
  { value: 'mistral', label: 'Mistral (Ollama)' },
]

const promptTypes = [
  { value: 'summary', label: 'Meeting Summary' },
  { value: 'email', label: 'Partner Email' },
  { value: 'training', label: 'Training Documentation' },
]

export default function Benchmark() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'transcription' | 'llm'>('transcription')
  
  // Transcription benchmark state
  const [selectedMediaId, setSelectedMediaId] = useState<number | null>(null)
  const [transcriptionModelA, setTranscriptionModelA] = useState('google-stt')
  const [transcriptionModelB, setTranscriptionModelB] = useState('whisper-large')
  
  // LLM benchmark state
  const [selectedTranscriptionId, setSelectedTranscriptionId] = useState<number | null>(null)
  const [selectedPromptType, setSelectedPromptType] = useState('summary')
  const [llmModelA, setLlmModelA] = useState('gemini-pro')
  const [llmModelB, setLlmModelB] = useState('gpt-4')

  // Fetch data
  const { data: mediaData } = useQuery({
    queryKey: ['media'],
    queryFn: () => mediaApi.list(),
  })

  const { data: transcriptionData } = useQuery({
    queryKey: ['transcriptions'],
    queryFn: () => transcriptionApi.list(),
  })

  const { data: benchmarkData, isLoading: loadingResults } = useQuery({
    queryKey: ['benchmarks'],
    queryFn: () => benchmarkApi.listResults(),
  })

  const media = mediaData?.data?.media || []
  const transcriptions = transcriptionData?.data?.transcriptions || []
  const benchmarkResults = benchmarkData?.data?.results || []

  const filteredResults = benchmarkResults.filter((r: any) =>
    activeTab === 'transcription'
      ? r.benchmark_type === 'transcription'
      : r.benchmark_type === 'llm_processing'
  )

  // Transcription benchmark mutation
  const transcriptionBenchmarkMutation = useMutation({
    mutationFn: (data: { media_id: number; model_a: string; model_b: string }) =>
      benchmarkApi.runTranscription(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['benchmarks'] })
      toast.success('Transcription benchmark complete!')
    },
    onError: () => toast.error('Benchmark failed'),
  })

  // LLM benchmark mutation
  const llmBenchmarkMutation = useMutation({
    mutationFn: (data: {
      transcription_id: number
      prompt_type: string
      model_a: string
      model_b: string
    }) => benchmarkApi.runLLM(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['benchmarks'] })
      toast.success('LLM benchmark complete!')
    },
    onError: () => toast.error('Benchmark failed'),
  })

  const handleRunTranscriptionBenchmark = () => {
    if (!selectedMediaId) {
      toast.error('Please select a media file')
      return
    }
    transcriptionBenchmarkMutation.mutate({
      media_id: selectedMediaId,
      model_a: transcriptionModelA,
      model_b: transcriptionModelB,
    })
  }

  const handleRunLLMBenchmark = () => {
    if (!selectedTranscriptionId) {
      toast.error('Please select a transcription')
      return
    }
    llmBenchmarkMutation.mutate({
      transcription_id: selectedTranscriptionId,
      prompt_type: selectedPromptType,
      model_a: llmModelA,
      model_b: llmModelB,
    })
  }

  const tabs = [
    { id: 'transcription', label: 'Transcription Models', icon: <Mic className="w-4 h-4" /> },
    { id: 'llm', label: 'LLM Processing', icon: <Brain className="w-4 h-4" /> },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-lunar-start">Benchmark</h1>
        <p className="text-lunar-end mt-1">Compare AI models to find the best fit for your needs</p>
      </div>

      {/* Tabs */}
      <Tabs
        tabs={tabs}
        activeTab={activeTab}
        onChange={(tab) => setActiveTab(tab as 'transcription' | 'llm')}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-4">
          <Card hover={false}>
            <h3 className="font-medium text-lunar-start mb-4">
              {activeTab === 'transcription' ? 'Transcription Benchmark' : 'LLM Benchmark'}
            </h3>

            {activeTab === 'transcription' ? (
              <div className="space-y-4">
                <Select
                  label="Audio/Video File"
                  options={media.map((m: any) => ({
                    value: m.id.toString(),
                    label: m.original_filename,
                  }))}
                  value={selectedMediaId?.toString() || ''}
                  onChange={(e) => setSelectedMediaId(parseInt(e.target.value))}
                  placeholder="Select a file"
                />
                <Select
                  label="Model A (Baseline)"
                  options={transcriptionModels}
                  value={transcriptionModelA}
                  onChange={(e) => setTranscriptionModelA(e.target.value)}
                />
                <Select
                  label="Model B (Challenger)"
                  options={transcriptionModels}
                  value={transcriptionModelB}
                  onChange={(e) => setTranscriptionModelB(e.target.value)}
                />
                <Button
                  className="w-full"
                  leftIcon={<Play className="w-4 h-4" />}
                  onClick={handleRunTranscriptionBenchmark}
                  loading={transcriptionBenchmarkMutation.isPending}
                  disabled={!selectedMediaId}
                >
                  Run Benchmark
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <Select
                  label="Transcription"
                  options={transcriptions.map((t: any) => ({
                    value: t.id.toString(),
                    label: t.title,
                  }))}
                  value={selectedTranscriptionId?.toString() || ''}
                  onChange={(e) => setSelectedTranscriptionId(parseInt(e.target.value))}
                  placeholder="Select a transcription"
                />
                <Select
                  label="Prompt Type"
                  options={promptTypes}
                  value={selectedPromptType}
                  onChange={(e) => setSelectedPromptType(e.target.value)}
                />
                <Select
                  label="Model A (Baseline - Gemini)"
                  options={llmModels}
                  value={llmModelA}
                  onChange={(e) => setLlmModelA(e.target.value)}
                />
                <Select
                  label="Model B (Challenger)"
                  options={llmModels}
                  value={llmModelB}
                  onChange={(e) => setLlmModelB(e.target.value)}
                />
                <Button
                  className="w-full"
                  leftIcon={<Play className="w-4 h-4" />}
                  onClick={handleRunLLMBenchmark}
                  loading={llmBenchmarkMutation.isPending}
                  disabled={!selectedTranscriptionId}
                >
                  Run Benchmark
                </Button>
              </div>
            )}
          </Card>

          {/* How it works */}
          <Card hover={false} gradient="stratos">
            <h4 className="font-medium text-lunar-start mb-2">How it works</h4>
            <p className="text-sm text-lunar-end">
              {activeTab === 'transcription'
                ? 'Both models transcribe the same audio. An LLM judge evaluates accuracy, completeness, and formatting to determine the winner.'
                : 'Both models process the same transcription with the chosen prompt. Gemini serves as the baseline, and an LLM judge scores quality, relevance, and style.'
              }
            </p>
          </Card>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-medium text-lunar-start">Recent Results</h3>

          {loadingResults ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          ) : filteredResults.length === 0 ? (
            <EmptyState
              icon={BarChart3}
              title="No benchmark results yet"
              description={`Run your first ${activeTab === 'transcription' ? 'transcription' : 'LLM'} benchmark to see results here`}
            />
          ) : (
            <div className="space-y-3">
              <AnimatePresence>
                {filteredResults.map((result: any, index: number) => (
                  <motion.div
                    key={result.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card className="cursor-pointer">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={cn(
                            'w-12 h-12 rounded-xl flex items-center justify-center',
                            result.score_a > result.score_b
                              ? 'bg-gradient-celestial'
                              : 'bg-gradient-solar'
                          )}>
                            <Trophy className={cn(
                              'w-6 h-6',
                              result.score_a > result.score_b ? 'text-eclipse-end' : 'text-white'
                            )} />
                          </div>
                          <div>
                            <h4 className="font-medium text-lunar-start">
                              {result.test_name}
                            </h4>
                            <div className="flex items-center gap-4 mt-1 text-sm text-lunar-end">
                              <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {formatDate(result.created_at)}
                              </span>
                            </div>
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-lunar-end" />
                      </div>

                      {/* Score comparison */}
                      <div className="mt-4 pt-4 border-t border-white/5">
                        <div className="grid grid-cols-2 gap-4">
                          <div className={cn(
                            'p-3 rounded-xl',
                            result.score_a > result.score_b
                              ? 'bg-celestial-start/10 border border-celestial-start/30'
                              : 'bg-white/5'
                          )}>
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-lunar-start">
                                {result.model_a}
                              </span>
                              {result.score_a > result.score_b && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-celestial-start text-eclipse-end">
                                  Winner
                                </span>
                              )}
                            </div>
                            <div className="text-2xl font-bold text-lunar-start">
                              {result.score_a?.toFixed(1) || 'N/A'}
                            </div>
                          </div>
                          <div className={cn(
                            'p-3 rounded-xl',
                            result.score_b > result.score_a
                              ? 'bg-celestial-start/10 border border-celestial-start/30'
                              : 'bg-white/5'
                          )}>
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-lunar-start">
                                {result.model_b}
                              </span>
                              {result.score_b > result.score_a && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-celestial-start text-eclipse-end">
                                  Winner
                                </span>
                              )}
                            </div>
                            <div className="text-2xl font-bold text-lunar-start">
                              {result.score_b?.toFixed(1) || 'N/A'}
                            </div>
                          </div>
                        </div>

                        {result.judge_reasoning && (
                          <div className="mt-3 p-3 rounded-lg bg-eclipse-start/50">
                            <p className="text-xs text-lunar-end">
                              <span className="font-medium text-lunar-start">Judge reasoning:</span>{' '}
                              {result.judge_reasoning}
                            </p>
                          </div>
                        )}
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
