import { forwardRef, HTMLAttributes } from 'react'
import { motion } from 'framer-motion'
import { cn } from '../../lib/utils'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  gradient?: 'eclipse' | 'stratos' | 'orbit' | 'lunar' | 'stardust'
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, hover = true, gradient = 'eclipse', children, ...props }, ref) => {
    const gradients = {
      eclipse: 'bg-gradient-eclipse',
      stratos: 'bg-gradient-stratos',
      orbit: 'bg-gradient-orbit',
      lunar: 'bg-gradient-lunar text-eclipse-end',
      stardust: 'bg-gradient-stardust text-eclipse-end',
    }

    return (
      <motion.div
        ref={ref}
        className={cn(
          'rounded-2xl border border-white/5 p-4',
          gradients[gradient],
          hover && 'card-hover cursor-pointer',
          className
        )}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        {...props}
      >
        {children}
      </motion.div>
    )
  }
)

Card.displayName = 'Card'

export default Card
