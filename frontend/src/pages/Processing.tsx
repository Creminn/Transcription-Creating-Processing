import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Wand2,
  FileText,
  Mail,
  GraduationCap,
  Calendar,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  Copy,
  Download,
  RefreshCw,
  Check,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Button, Card, Select, Toggle, Textarea, EmptyState, CardSkeleton } from '../components/ui'
import { processingApi, transcriptionApi, personaApi, templateApi } from '../services/api'
import { useAppStore } from '../store/appStore'
import { cn, truncateText } from '../lib/utils'

const promptTypes = [
  { value: 'summary', label: 'Meeting Summary', icon: FileText, description: 'Generate a concise summary of the meeting' },
  { value: 'email', label: 'Partner Email', icon: Mail, description: 'Create meeting notes email for partners' },
  { value: 'training', label: 'Training Documentation', icon: GraduationCap, description: 'Generate educational material' },
  { value: 'weekly', label: 'Weekly Summary', icon: Calendar, description: 'Aggregate multiple meetings into weekly summary' },
  { value: 'custom', label: 'Custom Prompt', icon: MessageSquare, description: 'Use your own custom prompt' },
]

const llmModels = [
  { value: 'gpt-4', label: 'GPT-4 (OpenAI)' },
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo (OpenAI)' },
  { value: 'gemini-pro', label: 'Gemini Pro (Google)' },
  { value: 'llama2', label: 'Llama 2 (Ollama)' },
  { value: 'mistral', label: 'Mistral (Ollama)' },
]

export default function Processing() {
  const { selectedTranscriptionIds } = useAppStore()
  const [selectedPrompt, setSelectedPrompt] = useState('summary')
  const [selectedModel, setSelectedModel] = useState('gpt-4')
  const [customPrompt, setCustomPrompt] = useState('')
  const [usePersona, setUsePersona] = useState(false)
  const [useTemplate, setUseTemplate] = useState(false)
  const [selectedPersonaId, setSelectedPersonaId] = useState<number | null>(null)
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null)
  const [output, setOutput] = useState<string | null>(null)
  const [showTranscriptions, setShowTranscriptions] = useState(true)
  const [copied, setCopied] = useState(false)

  // Fetch transcriptions
  const { data: transcriptionData, isLoading: loadingTranscriptions } = useQuery({
    queryKey: ['transcriptions'],
    queryFn: () => transcriptionApi.list(),
  })

  // Fetch personas
  const { data: personaData } = useQuery({
    queryKey: ['personas'],
    queryFn: () => personaApi.list(),
    enabled: usePersona,
  })

  // Fetch templates
  const { data: templateData } = useQuery({
    queryKey: ['templates'],
    queryFn: () => templateApi.list(),
    enabled: useTemplate,
  })

  const transcriptions = transcriptionData?.data?.transcriptions || []
  const personas = personaData?.data?.personas || []
  const templates = templateData?.data?.templates || []

  const selectedTranscriptions = transcriptions.filter((t: any) =>
    selectedTranscriptionIds.includes(t.id)
  )

  // Process mutation
  const processMutation = useMutation({
    mutationFn: (data: any) => processingApi.process(data),
    onSuccess: (response) => {
      setOutput(response.data.output_content)
      toast.success('Processing complete!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Processing failed')
    },
  })

  const handleProcess = () => {
    if (selectedTranscriptionIds.length === 0) {
      toast.error('Please select at least one transcription')
      return
    }

    processMutation.mutate({
      transcription_ids: selectedTranscriptionIds,
      prompt_type: selectedPrompt,
      llm_model: selectedModel,
      persona_id: usePersona ? selectedPersonaId : undefined,
      template_id: useTemplate ? selectedTemplateId : undefined,
      custom_prompt: selectedPrompt === 'custom' ? customPrompt : undefined,
    })
  }

  const handleCopy = async () => {
    if (output) {
      await navigator.clipboard.writeText(output)
      setCopied(true)
      toast.success('Copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownload = () => {
    if (output) {
      const blob = new Blob([output], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `output-${selectedPrompt}-${Date.now()}.txt`
      a.click()
      URL.revokeObjectURL(url)
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
      <div>
        <h1 className="text-2xl font-bold text-lunar-start">Process Transcriptions</h1>
        <p className="text-lunar-end mt-1">Generate summaries, emails, and documents from your transcriptions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Configuration */}
        <div className="space-y-6">
          {/* Selected Transcriptions */}
          <Card hover={false}>
            <button
              onClick={() => setShowTranscriptions(!showTranscriptions)}
              className="w-full flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-celestial flex items-center justify-center">
                  <FileText className="w-5 h-5 text-eclipse-end" />
                </div>
                <div className="text-left">
                  <h3 className="font-medium text-lunar-start">Selected Transcriptions</h3>
                  <p className="text-sm text-lunar-end">
                    {selectedTranscriptionIds.length} transcription(s) selected
                  </p>
                </div>
              </div>
              {showTranscriptions ? (
                <ChevronUp className="w-5 h-5 text-lunar-end" />
              ) : (
                <ChevronDown className="w-5 h-5 text-lunar-end" />
              )}
            </button>

            <AnimatePresence>
              {showTranscriptions && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden"
                >
                  <div className="mt-4 pt-4 border-t border-white/5 space-y-2 max-h-48 overflow-y-auto">
                    {selectedTranscriptions.length === 0 ? (
                      <p className="text-sm text-lunar-end text-center py-4">
                        No transcriptions selected. Go to the Transcriptions page to select some.
                      </p>
                    ) : (
                      selectedTranscriptions.map((t: any) => (
                        <div
                          key={t.id}
                          className="p-3 rounded-lg bg-eclipse-start/50 border border-white/5"
                        >
                          <p className="text-sm font-medium text-lunar-start">{t.title}</p>
                          <p className="text-xs text-lunar-end mt-1">
                            {truncateText(t.content, 100)}
                          </p>
                        </div>
                      ))
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>

          {/* Prompt Type */}
          <Card hover={false}>
            <h3 className="font-medium text-lunar-start mb-4">Prompt Type</h3>
            <div className="grid grid-cols-1 gap-2">
              {promptTypes.map((prompt) => (
                <button
                  key={prompt.value}
                  onClick={() => setSelectedPrompt(prompt.value)}
                  className={cn(
                    'flex items-center gap-3 p-3 rounded-xl text-left transition-all',
                    selectedPrompt === prompt.value
                      ? 'bg-gradient-solar text-white'
                      : 'bg-eclipse-start/50 text-lunar-end hover:bg-white/5 hover:text-lunar-start'
                  )}
                >
                  <prompt.icon className="w-5 h-5 flex-shrink-0" />
                  <div>
                    <p className="font-medium">{prompt.label}</p>
                    <p className={cn(
                      'text-xs',
                      selectedPrompt === prompt.value ? 'text-white/80' : 'text-lunar-end'
                    )}>
                      {prompt.description}
                    </p>
                  </div>
                </button>
              ))}
            </div>

            {selectedPrompt === 'custom' && (
              <div className="mt-4">
                <Textarea
                  label="Custom Prompt"
                  placeholder="Enter your custom prompt..."
                  rows={4}
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                />
              </div>
            )}
          </Card>

          {/* LLM Model */}
          <Card hover={false}>
            <Select
              label="LLM Model"
              options={llmModels}
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
            />
          </Card>

          {/* Personalization Options */}
          <Card hover={false}>
            <h3 className="font-medium text-lunar-start mb-4">Personalization (Optional)</h3>
            
            <div className="space-y-4">
              <Toggle
                label="Personalize with Persona"
                description="Apply a writing style from a saved persona"
                checked={usePersona}
                onChange={setUsePersona}
              />

              <AnimatePresence>
                {usePersona && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                  >
                    <Select
                      options={personas.map((p: any) => ({ value: p.id.toString(), label: p.name }))}
                      value={selectedPersonaId?.toString() || ''}
                      onChange={(e) => setSelectedPersonaId(parseInt(e.target.value))}
                      placeholder="Select a persona"
                    />
                  </motion.div>
                )}
              </AnimatePresence>

              <Toggle
                label="Use Email Template"
                description="Apply a saved email template structure"
                checked={useTemplate}
                onChange={setUseTemplate}
              />

              <AnimatePresence>
                {useTemplate && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                  >
                    <Select
                      options={templates.map((t: any) => ({ value: t.id.toString(), label: t.name }))}
                      value={selectedTemplateId?.toString() || ''}
                      onChange={(e) => setSelectedTemplateId(parseInt(e.target.value))}
                      placeholder="Select a template"
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </Card>

          {/* Generate Button */}
          <Button
            className="w-full"
            size="lg"
            leftIcon={<Wand2 className="w-5 h-5" />}
            onClick={handleProcess}
            loading={processMutation.isPending}
            disabled={selectedTranscriptionIds.length === 0}
          >
            Generate Output
          </Button>
        </div>

        {/* Right Column - Output */}
        <div className="space-y-4">
          <Card hover={false} className="min-h-[400px]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-lunar-start">Output</h3>
              {output && (
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    leftIcon={copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    onClick={handleCopy}
                  >
                    {copied ? 'Copied' : 'Copy'}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    leftIcon={<Download className="w-4 h-4" />}
                    onClick={handleDownload}
                  >
                    Download
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    leftIcon={<RefreshCw className="w-4 h-4" />}
                    onClick={handleProcess}
                    disabled={processMutation.isPending}
                  >
                    Regenerate
                  </Button>
                </div>
              )}
            </div>

            {processMutation.isPending ? (
              <div className="flex flex-col items-center justify-center py-16">
                <div className="w-12 h-12 rounded-full border-4 border-celestial-start/20 border-t-celestial-start animate-spin mb-4" />
                <p className="text-lunar-end">Generating output...</p>
              </div>
            ) : output ? (
              <div className="prose prose-invert max-w-none">
                <pre className="whitespace-pre-wrap font-sans text-sm text-lunar-start bg-eclipse-start/50 rounded-xl p-4">
                  {output}
                </pre>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="w-16 h-16 rounded-2xl bg-gradient-stratos flex items-center justify-center mb-4">
                  <Wand2 className="w-8 h-8 text-lunar-end" />
                </div>
                <p className="text-lunar-start font-medium">Ready to generate</p>
                <p className="text-lunar-end text-sm mt-1">
                  Select transcriptions and click Generate to see the output here
                </p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </motion.div>
  )
}
