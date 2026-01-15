import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FileCode,
  Plus,
  Edit2,
  Trash2,
  Info,
  Copy,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Button, Card, Input, Textarea, Select, Modal, EmptyState, Tabs, CardSkeleton } from '../components/ui'
import { templateApi } from '../services/api'
import { cn, truncateText, formatDate } from '../lib/utils'

const categories = [
  { value: 'meeting_notes', label: 'Meeting Notes' },
  { value: 'follow_up', label: 'Follow Up' },
  { value: 'summary', label: 'Summary' },
  { value: 'training', label: 'Training' },
  { value: 'custom', label: 'Custom' },
]

const placeholders = [
  { key: '{{meeting_date}}', description: 'Date of the meeting' },
  { key: '{{attendees}}', description: 'List of attendees' },
  { key: '{{summary}}', description: 'Generated meeting summary' },
  { key: '{{action_items}}', description: 'List of action items' },
  { key: '{{next_steps}}', description: 'Next steps from the meeting' },
  { key: '{{decisions}}', description: 'Key decisions made' },
  { key: '{{topics}}', description: 'Topics discussed' },
]

interface TemplateFormData {
  name: string
  category: string
  template_content: string
}

const initialFormData: TemplateFormData = {
  name: '',
  category: 'meeting_notes',
  template_content: '',
}

export default function Templates() {
  const queryClient = useQueryClient()
  const [activeCategory, setActiveCategory] = useState('all')
  const [showModal, setShowModal] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<TemplateFormData>(initialFormData)
  const [showPlaceholderGuide, setShowPlaceholderGuide] = useState(false)

  // Fetch templates
  const { data: templateData, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: () => templateApi.list(),
  })

  const templates = templateData?.data?.templates || []
  const filteredTemplates = activeCategory === 'all'
    ? templates
    : templates.filter((t: any) => t.category === activeCategory)

  // Create mutation
  const createMutation = useMutation({
    mutationFn: (data: TemplateFormData) => templateApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      toast.success('Template created successfully')
      closeModal()
    },
    onError: () => toast.error('Failed to create template'),
  })

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<TemplateFormData> }) =>
      templateApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      toast.success('Template updated successfully')
      closeModal()
    },
    onError: () => toast.error('Failed to update template'),
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => templateApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      toast.success('Template deleted')
    },
    onError: () => toast.error('Failed to delete template'),
  })

  const openCreateModal = () => {
    setEditingId(null)
    setFormData(initialFormData)
    setShowModal(true)
  }

  const openEditModal = (template: any) => {
    setEditingId(template.id)
    setFormData({
      name: template.name,
      category: template.category,
      template_content: template.template_content,
    })
    setShowModal(true)
  }

  const closeModal = () => {
    setShowModal(false)
    setEditingId(null)
    setFormData(initialFormData)
  }

  const handleSubmit = () => {
    if (!formData.name || !formData.template_content) {
      toast.error('Please fill in all required fields')
      return
    }

    if (editingId) {
      updateMutation.mutate({ id: editingId, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const insertPlaceholder = (placeholder: string) => {
    setFormData({
      ...formData,
      template_content: formData.template_content + placeholder,
    })
  }

  const tabs = [
    { id: 'all', label: 'All', count: templates.length },
    ...categories.map((cat) => ({
      id: cat.value,
      label: cat.label,
      count: templates.filter((t: any) => t.category === cat.value).length,
    })),
  ]

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
          <h1 className="text-2xl font-bold text-lunar-start">Email Templates</h1>
          <p className="text-lunar-end mt-1">Create reusable templates with placeholders</p>
        </div>
        <Button
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={openCreateModal}
        >
          Create Template
        </Button>
      </div>

      {/* Tabs */}
      <div className="overflow-x-auto">
        <Tabs
          tabs={tabs}
          activeTab={activeCategory}
          onChange={setActiveCategory}
        />
      </div>

      {/* Templates Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : filteredTemplates.length === 0 ? (
        <EmptyState
          icon={FileCode}
          title="No templates yet"
          description={activeCategory === 'all'
            ? 'Create your first template to streamline email generation'
            : `No templates in ${categories.find(c => c.value === activeCategory)?.label} category`
          }
          action={activeCategory === 'all' ? {
            label: 'Create Template',
            onClick: openCreateModal,
          } : undefined}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <AnimatePresence>
            {filteredTemplates.map((template: any, index: number) => (
              <motion.div
                key={template.id}
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
                        openEditModal(template)
                      }}
                      className="p-2 rounded-lg hover:bg-white/5 text-lunar-end hover:text-lunar-start transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteMutation.mutate(template.id)
                      }}
                      className="p-2 rounded-lg hover:bg-red-600/20 text-lunar-end hover:text-red-500 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-stardust flex items-center justify-center flex-shrink-0">
                      <FileCode className="w-6 h-6 text-eclipse-end" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-lunar-start">{template.name}</h3>
                      <span className="inline-block mt-1 px-2 py-0.5 text-xs rounded-full bg-celestial-start/20 text-celestial-start">
                        {categories.find(c => c.value === template.category)?.label}
                      </span>
                    </div>
                  </div>

                  <div className="mt-4">
                    <pre className="text-xs text-lunar-end bg-eclipse-start/50 rounded-lg p-3 overflow-hidden max-h-24 whitespace-pre-wrap font-sans">
                      {truncateText(template.template_content, 200)}
                    </pre>
                  </div>

                  <div className="mt-4 pt-4 border-t border-white/5 text-xs text-lunar-end">
                    Created {formatDate(template.created_at)}
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
        title={editingId ? 'Edit Template' : 'Create Template'}
        size="lg"
      >
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Template Name"
              placeholder="e.g., Weekly Meeting Summary"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
            <Select
              label="Category"
              options={categories}
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium text-lunar-start">
                Template Content
              </label>
              <Button
                variant="ghost"
                size="sm"
                leftIcon={<Info className="w-4 h-4" />}
                onClick={() => setShowPlaceholderGuide(!showPlaceholderGuide)}
              >
                Placeholders
              </Button>
            </div>

            <AnimatePresence>
              {showPlaceholderGuide && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden"
                >
                  <div className="p-4 rounded-xl bg-eclipse-start/50 border border-white/5 mb-3">
                    <p className="text-xs text-lunar-end mb-3">
                      Click on a placeholder to insert it into your template:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {placeholders.map((p) => (
                        <button
                          key={p.key}
                          onClick={() => insertPlaceholder(p.key)}
                          className="px-2 py-1 text-xs rounded-lg bg-celestial-start/20 text-celestial-start hover:bg-celestial-start/30 transition-colors"
                          title={p.description}
                        >
                          {p.key}
                        </button>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <Textarea
              placeholder="Subject: Meeting Notes - {{meeting_date}}

Hi team,

Here's a summary of our meeting:

{{summary}}

Action Items:
{{action_items}}

Next Steps:
{{next_steps}}

Best regards"
              rows={12}
              value={formData.template_content}
              onChange={(e) => setFormData({ ...formData, template_content: e.target.value })}
            />
          </div>

          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={closeModal}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              loading={createMutation.isPending || updateMutation.isPending}
            >
              {editingId ? 'Save Changes' : 'Create Template'}
            </Button>
          </div>
        </div>
      </Modal>
    </motion.div>
  )
}
