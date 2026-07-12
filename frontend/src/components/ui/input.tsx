'use client'

import { forwardRef, useState, InputHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'
import { motion, AnimatePresence } from 'framer-motion'
import { Check } from 'lucide-react'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  showCharCount?: boolean
  maxLength?: number
  success?: boolean
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, leftIcon, rightIcon, showCharCount, maxLength, success, value, onChange, ...props }, ref) => {
    const [focused, setFocused] = useState(false)

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (maxLength && e.target.value.length > maxLength) return
      onChange?.(e)
    }

    return (
      <div className="w-full">
        {label && (
          <motion.label
            initial={false}
            animate={{ y: focused || (value as string)?.length ? -4 : 0 }}
            className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300"
          >
            {label}
          </motion.label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="pointer-events-none absolute inset-y-0 left-0 z-10 flex items-center pl-3 text-neutral-400">
              {leftIcon}
            </div>
          )}
          <motion.div
            animate={error ? { x: [0, -4, 4, -4, 4, 0] } : {}}
            transition={{ duration: 0.3 }}
          >
            <input
              type={type}
              className={cn(
                'flex h-10 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200',
                error && 'border-red-500 focus-visible:ring-red-500',
                success && 'border-emerald-500 pr-10',
                leftIcon && 'pl-10',
                rightIcon && 'pr-10',
                className
              )}
              ref={ref}
              value={value}
              onChange={handleChange}
              onFocus={(e) => { setFocused(true); props.onFocus?.(e) }}
              onBlur={(e) => { setFocused(false); props.onBlur?.(e) }}
              aria-invalid={!!error}
              aria-describedby={error ? `${props.id || 'input'}-error` : undefined}
              {...props}
            />
          </motion.div>
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 z-10 flex items-center pr-3 text-neutral-400">
              {rightIcon}
            </div>
          )}
          {success && !rightIcon && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute inset-y-0 right-0 z-10 flex items-center pr-3"
            >
              <Check className="h-4 w-4 text-emerald-500" />
            </motion.div>
          )}
          {focused && (
            <motion.div
              layoutId="input-glow"
              className="pointer-events-none absolute -inset-0.5 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 opacity-20 blur-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.2 }}
              exit={{ opacity: 0 }}
            />
          )}
        </div>
        <div className="flex items-center justify-between">
          <AnimatePresence>
            {error && (
              <motion.p
                key="error"
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                id={`${props.id || 'input'}-error`}
                className="mt-1 text-xs text-red-500"
                role="alert"
              >
                {error}
              </motion.p>
            )}
          </AnimatePresence>
          {showCharCount && maxLength && (
            <span className="mt-1 text-xs text-muted-foreground">
              {(value as string)?.length || 0}/{maxLength}
            </span>
          )}
        </div>
      </div>
    )
  }
)
Input.displayName = 'Input'

export { Input }
