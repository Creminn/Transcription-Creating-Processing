import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import Sidebar from './Sidebar'
import { useAppStore } from '../store/appStore'
import { cn } from '../lib/utils'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { sidebarCollapsed } = useAppStore()
  console.log('Layout component rendering, sidebarCollapsed:', sidebarCollapsed)

  return (
    <div className="flex h-screen bg-gradient-eclipse overflow-hidden">
      <Sidebar />
      <motion.main
        className={cn(
          'flex-1 overflow-auto transition-all duration-300',
          sidebarCollapsed ? 'ml-20' : 'ml-64'
        )}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <div className="min-h-full p-6">
          {children}
        </div>
      </motion.main>
    </div>
  )
}
