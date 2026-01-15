import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Settings as SettingsIcon,
  Key,
  Server,
  HardDrive,
  Palette,
  Check,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Button, Card, Input, Select, Toggle } from '../components/ui'
import { cn } from '../lib/utils'

const colorSchemes = [
  { id: 'solar', name: 'Solar', start: '#E92E2F', end: '#FF6126' },
  { id: 'eclipse', name: 'Eclipse', start: '#261A28', end: '#18181B' },
  { id: 'lunar', name: 'Lunar', start: '#EFEBE4', end: '#D0C2C7' },
  { id: 'celestial', name: 'Celestial', start: '#2EDFE2', end: '#71F3A7' },
  { id: 'stratos', name: 'Stratos', start: '#44221E', end: '#18181B' },
  { id: 'cosmic', name: 'Cosmic', start: '#EFEBE4', end: '#F0CABF' },
  { id: 'orbit', name: 'Orbit', start: '#23423D', end: '#18181B' },
  { id: 'stardust', name: 'Stardust', start: '#EFEBE4', end: '#CFEBDD' },
]

export default function Settings() {
  const [selectedTheme, setSelectedTheme] = useState('eclipse')
  const [settings, setSettings] = useState({
    openai_api_key: '',
    google_gemini_api_key: '',
    google_service_account: '',
    google_drive_email: '',
    ollama_host: 'http://localhost:11434',
    whisper_model_size: 'base',
    max_upload_size: 500,
    auto_convert: true,
    default_language: 'en',
  })

  const handleSave = () => {
    toast.success('Settings saved successfully')
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6 max-w-4xl"
    >
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-lunar-start">Settings</h1>
        <p className="text-lunar-end mt-1">Configure API keys and application preferences</p>
      </div>

      {/* API Keys */}
      <Card hover={false}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-solar flex items-center justify-center">
            <Key className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-medium text-lunar-start">API Keys</h3>
            <p className="text-sm text-lunar-end">Connect to AI services</p>
          </div>
        </div>

        <div className="space-y-4">
          <Input
            label="OpenAI API Key"
            type="password"
            placeholder="sk-..."
            value={settings.openai_api_key}
            onChange={(e) => setSettings({ ...settings, openai_api_key: e.target.value })}
          />
          <Input
            label="Google Gemini API Key"
            type="password"
            placeholder="AIza..."
            value={settings.google_gemini_api_key}
            onChange={(e) => setSettings({ ...settings, google_gemini_api_key: e.target.value })}
          />
        </div>
      </Card>

      {/* Google Drive */}
      <Card hover={false}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-celestial flex items-center justify-center">
            <HardDrive className="w-5 h-5 text-eclipse-end" />
          </div>
          <div>
            <h3 className="font-medium text-lunar-start">Google Drive Integration</h3>
            <p className="text-sm text-lunar-end">Download meeting recordings directly</p>
          </div>
        </div>

        <div className="space-y-4">
          <Input
            label="Service Account JSON Path"
            placeholder="./credentials/service-account.json"
            value={settings.google_service_account}
            onChange={(e) => setSettings({ ...settings, google_service_account: e.target.value })}
          />
          <Input
            label="Service Account Email"
            placeholder="your-service@project.iam.gserviceaccount.com"
            value={settings.google_drive_email}
            onChange={(e) => setSettings({ ...settings, google_drive_email: e.target.value })}
          />
          <div className="p-3 rounded-lg bg-celestial-start/10 border border-celestial-start/20">
            <p className="text-sm text-lunar-end">
              Share your Google Drive files with this email to allow the app to download them.
            </p>
          </div>
        </div>
      </Card>

      {/* Local Models */}
      <Card hover={false}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-orbit flex items-center justify-center">
            <Server className="w-5 h-5 text-lunar-start" />
          </div>
          <div>
            <h3 className="font-medium text-lunar-start">Local Models</h3>
            <p className="text-sm text-lunar-end">Configure Whisper and Ollama</p>
          </div>
        </div>

        <div className="space-y-4">
          <Input
            label="Ollama Host"
            placeholder="http://localhost:11434"
            value={settings.ollama_host}
            onChange={(e) => setSettings({ ...settings, ollama_host: e.target.value })}
          />
          <Select
            label="Default Whisper Model"
            options={[
              { value: 'tiny', label: 'Tiny (fastest)' },
              { value: 'base', label: 'Base' },
              { value: 'small', label: 'Small' },
              { value: 'medium', label: 'Medium' },
              { value: 'large', label: 'Large (most accurate)' },
            ]}
            value={settings.whisper_model_size}
            onChange={(e) => setSettings({ ...settings, whisper_model_size: e.target.value })}
          />
        </div>
      </Card>

      {/* Preferences */}
      <Card hover={false}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-stratos flex items-center justify-center">
            <SettingsIcon className="w-5 h-5 text-lunar-end" />
          </div>
          <div>
            <h3 className="font-medium text-lunar-start">Preferences</h3>
            <p className="text-sm text-lunar-end">Application settings</p>
          </div>
        </div>

        <div className="space-y-4">
          <Input
            label="Max Upload Size (MB)"
            type="number"
            value={settings.max_upload_size.toString()}
            onChange={(e) => setSettings({ ...settings, max_upload_size: parseInt(e.target.value) || 500 })}
          />
          <Select
            label="Default Language"
            options={[
              { value: 'en', label: 'English' },
              { value: 'tr', label: 'Turkish' },
              { value: 'de', label: 'German' },
              { value: 'fr', label: 'French' },
              { value: 'es', label: 'Spanish' },
            ]}
            value={settings.default_language}
            onChange={(e) => setSettings({ ...settings, default_language: e.target.value })}
          />
          <Toggle
            label="Auto-convert MP4 to MP3"
            description="Automatically extract audio from video files"
            checked={settings.auto_convert}
            onChange={(checked) => setSettings({ ...settings, auto_convert: checked })}
          />
        </div>
      </Card>

      {/* Color Scheme */}
      <Card hover={false}>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-cosmic flex items-center justify-center">
            <Palette className="w-5 h-5 text-eclipse-end" />
          </div>
          <div>
            <h3 className="font-medium text-lunar-start">Color Scheme</h3>
            <p className="text-sm text-lunar-end">Choose your preferred theme</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {colorSchemes.map((scheme) => (
            <button
              key={scheme.id}
              onClick={() => setSelectedTheme(scheme.id)}
              className={cn(
                'relative p-3 rounded-xl border transition-all',
                selectedTheme === scheme.id
                  ? 'border-celestial-start'
                  : 'border-white/10 hover:border-white/20'
              )}
            >
              <div
                className="w-full h-8 rounded-lg mb-2"
                style={{
                  background: `linear-gradient(135deg, ${scheme.start}, ${scheme.end})`,
                }}
              />
              <span className="text-sm text-lunar-start">{scheme.name}</span>
              {selectedTheme === scheme.id && (
                <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-celestial-start flex items-center justify-center">
                  <Check className="w-3 h-3 text-eclipse-end" />
                </div>
              )}
            </button>
          ))}
        </div>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave}>
          Save Settings
        </Button>
      </div>
    </motion.div>
  )
}
