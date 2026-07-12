'use client'

import { forwardRef, useState, ButtonHTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'
import { Loader2, Check, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 relative overflow-hidden [--ripple-color:rgba(255,255,255,0.3)] active:scale-[0.98]',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-indigo-500/20',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-lg px-3 text-xs',
        lg: 'h-12 rounded-xl px-6 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, disabled, children, onClick, ...props }, ref) => {
    const [state, setState] = useState<'idle' | 'success' | 'error'>('idle')

    const handleClick = async (e: React.MouseEvent<HTMLButtonElement>) => {
      if (loading || disabled) return
      setState('idle')
      onClick?.(e)
    }

    return (
      <motion.button
        whileTap={{ scale: 0.97 }}
        whileHover={{ scale: 1.01 }}
        className={cn(
          buttonVariants({ variant, size, className }),
          state === 'success' && '!bg-emerald-500 !shadow-lg !shadow-emerald-500/30',
          state === 'error' && '!bg-red-500 !shadow-lg !shadow-red-500/30'
        )}
        ref={ref}
        disabled={disabled || loading}
        onClick={handleClick}
        aria-label={props['aria-label'] || (typeof children === 'string' ? children as string : undefined)}
        {...(props as any)}
      >
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.span
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center"
            >
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {children}
            </motion.span>
          ) : state === 'success' ? (
            <motion.span
              key="success"
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center"
            >
              <Check className="mr-2 h-4 w-4" />
              Done
            </motion.span>
          ) : state === 'error' ? (
            <motion.span
              key="error"
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center"
            >
              <X className="mr-2 h-4 w-4" />
              Failed
            </motion.span>
          ) : (
            <motion.span
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center"
            >
              {children}
            </motion.span>
          )}
        </AnimatePresence>
        <div className="pointer-events-none absolute inset-0 rounded-xl ring-2 ring-transparent focus-visible:ring-indigo-400/50 focus-visible:ring-offset-2" />
      </motion.button>
    )
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }
