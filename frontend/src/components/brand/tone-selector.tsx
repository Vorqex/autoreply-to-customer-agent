'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import {
  Briefcase,
  Smile,
  Sparkles,
  Building2,
  FileText,
  Hand,
  Heart,
  PartyPopper,
  Minus,
  Crown,
  Hotel,
  Stethoscope,
  type LucideIcon,
} from 'lucide-react'

export interface ToneOption {
  value: string
  label: string
  description: string
  icon: string
}

interface ToneSelectorProps {
  value: string
  onChange: (value: string) => void
  options: ToneOption[]
}

const iconMap: Record<string, LucideIcon> = {
  Briefcase,
  Smile,
  Sparkles,
  Building2,
  FileText,
  Hand,
  Heart,
  PartyPopper,
  Minus,
  Crown,
  Hotel,
  Stethoscope,
}

export function ToneSelector({ value, onChange, options }: ToneSelectorProps) {
  return (
    <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 lg:grid-cols-6">
      {options.map((tone) => {
        const Icon = iconMap[tone.icon] || Briefcase
        const isActive = value === tone.value

        return (
          <motion.button
            key={tone.value}
            type="button"
            onClick={() => onChange(tone.value)}
            layoutId={`tone-${tone.value}`}
            className={cn(
              'relative flex flex-col items-center gap-1.5 rounded-xl border p-3 text-xs transition-all',
              isActive
                ? 'border-indigo-500 bg-indigo-50 text-indigo-700 shadow-sm dark:border-indigo-400 dark:bg-indigo-950/50 dark:text-indigo-300'
                : 'border-input hover:bg-accent hover:border-muted-foreground/30 text-muted-foreground'
            )}
          >
            {isActive && (
              <motion.div
                layoutId="tone-active-bg"
                className="absolute inset-0 rounded-xl bg-indigo-50 dark:bg-indigo-950/30"
                transition={{ type: 'spring', stiffness: 400, damping: 30 }}
              />
            )}
            <div
              className={cn(
                'relative z-10 rounded-lg p-2 transition-colors',
                isActive
                  ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900 dark:text-indigo-300'
                  : 'bg-muted text-muted-foreground'
              )}
            >
              {Icon && <Icon className="h-4 w-4" />}
            </div>
            <span className="relative z-10 font-medium text-center">{tone.label}</span>
            {tone.description && (
              <span className="relative z-10 text-[10px] text-center leading-tight opacity-70">
                {tone.description}
              </span>
            )}
          </motion.button>
        )
      })}
    </div>
  )
}
