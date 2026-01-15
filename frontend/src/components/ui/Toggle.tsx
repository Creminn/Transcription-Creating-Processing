import { motion } from 'framer-motion'
import { cn } from '../../lib/utils'

interface ToggleProps {
  checked: boolean
  onChange: (checked: boolean) => void
  label?: string
  description?: string
  disabled?: boolean
}

export default function Toggle({
  checked,
  onChange,
  label,
  description,
  disabled = false,
}: ToggleProps) {
  return (
    <label
      className={cn(
        'flex items-start gap-3 cursor-pointer',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange(!checked)}
        className={cn(
          'relative inline-flex h-6 w-11 flex-shrink-0 rounded-full',
          'transition-colors duration-200 ease-in-out',
          'focus:outline-none focus:ring-2 focus:ring-celestial-start/50 focus:ring-offset-2 focus:ring-offset-eclipse-end',
          checked ? 'bg-gradient-celestial' : 'bg-eclipse-start border border-white/20'
        )}
      >
        <motion.span
          className={cn(
            'pointer-events-none inline-block h-5 w-5 rounded-full shadow-lg',
            'transform ring-0',
            checked ? 'bg-eclipse-end' : 'bg-lunar-end'
          )}
          animate={{
            x: checked ? 20 : 2,
            y: 2,
          }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        />
      </button>
      {(label || description) && (
        <div className="flex flex-col">
          {label && (
            <span className="text-sm font-medium text-lunar-start">{label}</span>
          )}
          {description && (
            <span className="text-xs text-lunar-end">{description}</span>
          )}
        </div>
      )}
    </label>
  )
}
