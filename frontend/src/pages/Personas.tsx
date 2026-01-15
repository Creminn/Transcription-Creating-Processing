import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Users,
  Plus,
  Edit2,
  Trash2,
  Mail,
  HelpCircle,
  Sparkles,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Button, Card, Input, Textarea, Modal, EmptyState, CardSkeleton } from '../components/ui'
import { personaApi } from '../services/api'
import { cn, truncateText } from '../lib/utils'

interface PersonaFormData {
  name: string
  sample_emails: string[]
  style_description: string
}

const initialFormData: PersonaFormData = {
  name: '',
  sample_emails: ['', '', ''],
  style_description: '',
}

export default function Personas() {
  const queryClient = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<PersonaFormData>(initialFormData)
  const [showGuidance, setShowGuidance] = useState(false)

  // Fetch personas
  const { data: personaData, isLoading } = useQuery({
    queryKey: ['personas'],
    queryFn: () => personaApi.list(),
  })

  const personas = personaData?.data?.personas || []

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: PersonaFormData) => personaApi.create({
      ...data,
      sample_emails: data.sample_emails.filter(e => e.trim() !== ''),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['personas'] })
      toast.success('Persona created successfully')
      closeModal()
    },
    onError: () => toast.error('Failed to create persona'),
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<PersonaFormData> }) =>
      personaApi.update(id, {
        ...data,
        sample_emails: data.sample_emails?.filter(e => e.trim() !== ''),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['personas'] })
      toast.success('Persona updated successfully')
      closeModal()
    },
    onError: () => toast.error('Failed to update persona'),
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => personaApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['personas'] })
      toast.success('Persona deleted')
    },
    onError: () => toast.error('Failed to delete persona'),
  })

  const openCreateModal = () => {
    setEditingId(null)
    setFormData(initialFormData)
    setShowModal(true)
  }

  const openEditModal = (persona: any) => {
    setEditingId(persona.id)
    setFormData({
      name: persona.name,
      sample_emails: [...persona.sample_emails, '', ''].slice(0, 5),
      style_description: persona.style_description,
    })
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingId(null)
    setFormData(initialFormData)
  }

  const handleSubmit = () => {
    if (!formData.name || !formData.style_description) {
      toast.error('Please fill in all required fields')
      return
    }

    if (editingId) {
      updateMutation.mutate({ id: editingId, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const updateSampleEmail = (index: number, value: string) => {
    const updated = [...formData.sample_emails]
    updated[index] = value
    setFormData({ ...formData, sample_emails: updated })
  }

  const addEmailSlot = () => {
    if (formData.sample_emails.length < 5) {
      setFormData({
        ...formData,
        sample_emails: [...formData.sample_emails, ''],
      })
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
          <h1 className="text-2xl font-bold text-lunar-start">Personas</h1>
          <p className="text-lunar-end mt-1">Create writing style personas for email personalization</p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            leftIcon={<HelpCircle className="w-4 h-4" />}
            onClick={() => setShowGuidance(true)}
          >
            How it works
          </Button>
          <Button
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={openCreateModal}
          >
            Create Persona
          </Button>
        </div>
      </div>

      {/* Personas Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : personas.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No personas yet"
          description="Create a persona to personalize your email outputs with a consistent writing style"
          action={{
            label: 'Create Persona',
            onClick: openCreateModal,
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {personas.map((persona: any, index: number) => (
              <motion.div
                key={persona.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="relative group h-full">
                  {/* Actions */}
                  <div className="absolute top-3 right-3 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        openEditModal(persona)
                      }}
                      className="p-2 rounded-lg hover:bg-white/5 text-lunar-end hover:text-lunar-start transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteMutation.mutate(persona.id)
                      }}
                      className="p-2 rounded-lg hover:bg-red-600/20 text-lunar-end hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-cosmic flex items-center justify-center flex-shrink-0">
                      <Users className="w-6 h-6 text-eclipse-end" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-lunar-start">{persona.name}</h3>
                      <p className="text-sm text-lunar-end mt-1 line-clamp-3">
                        {truncateText(persona.style_description, 120)}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-white/5">
                    <div className="flex items-center gap-2 text-xs text-lunar-end">
                      <Mail className="w-3 h-3" />
                      <span>{persona.sample_emails?.length || 0} sample emails</span>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showModal}
        onClose={closeModal}
        title={editingId ? 'Edit Persona' : 'Create Persona'}
        size="lg"
      >
        <div className="space-y-6">
          <Input
            label="Persona Name"
            placeholder="e.g., Zeynep's Style"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-lunar-start">
                Sample Emails (3-5 recommended)
              </label>
              {formData.sample_emails.length < 5 && (
                <Button variant="ghost" size="sm" onClick={addEmailSlot}>
                  Add another
                </Button>
              )}
            </div>
            <p className="text-xs text-lunar-end">
              Paste examples of emails written by this person to capture their writing style
            </p>
            {formData.sample_emails.map((email, index) => (
              <Textarea
                key={index}
                placeholder={`Sample email ${index + 1}...`}
                rows={3}
                value={email}
                onChange={(e) => updateSampleEmail(index, e.target.value)}
              />
            ))}
          </div>

          <Textarea
            label="Style Description"
            placeholder="Describe the writing style: tone, formality, common phrases, signature style..."
            rows={4}
            value={formData.style_description}
            onChange={(e) => setFormData({ ...formData, style_description: e.target.value })}
          />

          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={closeModal}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              loading={createMutation.isPending || updateMutation.isPending}
            >
              {editingId ? 'Save Changes' : 'Create Persona'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Guidance Modal */}
      <Modal
        isOpen={showGuidance}
        onClose={() => setShowGuidance(false)}
        title="How to Create Effective Personas"
        size="lg"
      >
        <div className="space-y-6 text-lunar-start">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-celestial flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-5 h-5 text-eclipse-end" />
            </div>
            <div>
              <h4 className="font-medium">What are Personas?</h4>
              <p className="text-sm text-lunar-end mt-1">
                Personas capture a person's unique writing style. When applied to generated emails,
                the AI will mimic their tone, vocabulary, and communication patterns.
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="font-medium">Best Practices:</h4>
            <ul className="space-y-2 text-sm text-lunar-end">
              <li className="flex items-start gap-2">
                <span className="text-celestial-start">1.</span>
                <span>Include 3-5 diverse email samples that represent different contexts (formal updates, casual check-ins, etc.)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-celestial-start">2.</span>
                <span>Choose emails that showcase signature phrases, greetings, and sign-offs</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-celestial-start">3.</span>
                <span>In the style description, note specific traits: "Uses bullet points, starts with 'Hi team', ends with 'Best'"</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-celestial-start">4.</span>
                <span>Mention formality level: casual, professional, friendly-professional</span>
              </li>
            </ul>
          </div>

          <div className="p-4 rounded-xl bg-eclipse-start/50 border border-white/5">
            <h4 className="font-medium text-sm mb-2">Example Style Description:</h4>
            <p className="text-xs text-lunar-end">
              "Zeynep writes in a warm, professional tone. She uses concise sentences and bullet points
              for clarity. Typically starts emails with 'Hi [name]' and ends with 'Best regards' or
              just 'Best'. Often includes a friendly closing line like 'Let me know if you have questions!'
              Uses exclamation marks sparingly but effectively."
            </p>
          </div>

          <Button className="w-full" onClick={() => setShowGuidance(false)}>
            Got it!
          </Button>
        </div>
      </Modal>
    </motion.div>
  )
}
