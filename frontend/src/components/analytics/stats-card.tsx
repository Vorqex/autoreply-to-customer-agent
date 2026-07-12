'use client'

import { useEffect, useState, type ReactNode } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Skeleton } from '@/components/ui/skeleton'

interface StatsCardProps {
  title: string
  value: number | string
  trend?: 'positive' | 'negative' | 'neutral'
  trendLabel?: string
  icon?: ReactNode
  loading?: boolean
  className?: string
  format?: 'number' | 'percentage' | 'duration'
}

export function StatsCard({
  title,
  value,
  trend,
  trendLabel,
  icon,
  loading,
  className,
  format = 'number',
}: StatsCardProps) {
  const [displayValue, setDisplayValue] = useState(0)
  const numericValue = typeof value === 'number' ? value : parseFloat(value as string) || 0

  useEffect(() => {
    if (loading || isNaN(numericValue)) return
    const duration = 800
    const steps = 30
    const increment = numericValue / steps
    let current = 0
    let step = 0
    const timer = setInterval(() => {
      step++
      current = Math.min(increment * step, numericValue)
      setDisplayValue(current)
      if (step >= steps) {
        clearInterval(timer)
        setDisplayValue(numericValue)
      }
    }, duration / steps)
    return () => clearInterval(timer)
  }, [numericValue, loading])

  const formatValue = (val: number) => {
    if (format === 'percentage') return `${Math.round(val)}%`
    if (format === 'duration') {
      const mins = Math.round(val)
      if (mins < 60) return `${mins}m`
      const hrs = Math.floor(mins / 60)
      const remain = mins % 60
      return `${hrs}h ${remain}m`
    }
    if (val >= 1000) {
      const k = val / 1000
      return `${k.toFixed(1)}k`
    }
    return Math.round(val).toLocaleString()
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={cn(
        'group relative overflow-hidden rounded-2xl border bg-card/80 backdrop-blur-xl p-6 shadow-sm transition-all duration-300 hover:shadow-md',
        className
      )}
    >
      {loading ? (
        <div className="space-y-3">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-3 w-32" />
        </div>
      ) : (
        <>
          <div className="flex items-start justify-between">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            {icon && (
              <div className="rounded-xl bg-primary/10 p-2.5 text-primary transition-colors group-hover:bg-primary/15">
                {icon}
              </div>
            )}
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold tracking-tight text-foreground">
              {formatValue(displayValue)}
            </span>
            {trend && (
              <div
                className={cn(
                  'inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 text-xs font-medium',
                  trend === 'positive' && 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400',
                  trend === 'negative' && 'bg-red-100 text-red-700 dark:bg-red-950/50 dark:text-red-400',
                  trend === 'neutral' && 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-400'
                )}
              >
                {trend === 'positive' && <TrendingUp className="h-3 w-3" />}
                {trend === 'negative' && <TrendingDown className="h-3 w-3" />}
                {trend === 'neutral' && <Minus className="h-3 w-3" />}
                {trendLabel}
              </div>
            )}
          </div>
          {trendLabel && (
            <p className="mt-1 text-xs text-muted-foreground">{trendLabel}</p>
          )}
        </>
      )}
      <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-gradient-to-br from-primary/5 via-primary/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
    </motion.div>
  )
}
