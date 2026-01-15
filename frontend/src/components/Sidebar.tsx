import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Video,
  FileText,
  Wand2,
  Users,
  FileCode,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react'
import { useAppStore } from '../store/appStore'
import { cn } from '../lib/utils'

const navItems = [
  { path: '/media', icon: Video, label: 'Media Library' },
  { path: '/transcriptions', icon: FileText, label: 'Transcriptions' },
  { path: '/process', icon: Wand2, label: 'Process' },
  { path: '/personas', icon: Users, label: 'Personas' },
  { path: '/templates', icon: FileCode, label: 'Templates' },
  { path: '/benchmark', icon: BarChart3, label: 'Benchmark' },
  { path: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useAppStore()
  const location = useLocation()

  return (
    <motion.aside
      className={cn(
        'fixed left-0 top-0 h-full bg-gradient-orbit z-50',
        'flex flex-col border-r border-white/5',
        'transition-all duration-300'
      )}
      animate={{ width: sidebarCollapsed ? 80 : 256 }}
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-white/5">
        <motion.div
          className="flex items-center gap-3"
          animate={{ justifyContent: sidebarCollapsed ? 'center' : 'flex-start' }}
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-solar flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.span
                className="font-bold text-lunar-start whitespace-nowrap"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
              >
                MeetingAI
              </motion.span>
            )}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 px-3 py-3 rounded-xl',
                'transition-all duration-200 group relative',
                isActive
                  ? 'bg-gradient-solar text-white shadow-lg shadow-solar-start/20'
                  : 'text-lunar-end hover:bg-white/5 hover:text-lunar-start'
              )}
            >
              <item.icon className={cn('w-5 h-5 flex-shrink-0', isActive && 'text-white')} />
              <AnimatePresence>
                {!sidebarCollapsed && (
                  <motion.span
                    className="whitespace-nowrap"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    transition={{ duration: 0.2 }}
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
              
              {/* Tooltip for collapsed state */}
              {sidebarCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-eclipse-start rounded-lg text-sm text-lunar-start whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                  {item.label}
                </div>
              )}
            </NavLink>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="p-3 border-t border-white/5">
        <button
          onClick={toggleSidebar}
          className={cn(
            'w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl',
            'text-lunar-end hover:bg-white/5 hover:text-lunar-start',
            'transition-all duration-200'
          )}
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <>
              <ChevronLeft className="w-5 h-5" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>
    </motion.aside>
  )
}
