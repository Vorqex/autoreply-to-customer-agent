'use client'

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { cn } from '@/lib/utils'

interface RatingRingProps {
  rating: number
  maxRating?: number
  label?: string
  size?: number
  strokeWidth?: number
  className?: string
}

export function RatingRing({
  rating,
  maxRating = 5,
  label = 'Average Rating',
  size = 160,
  strokeWidth = 10,
  className,
}: RatingRingProps) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  const percentage = (rating / maxRating) * 100
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (percentage / 100) * circumference

  const color =
    rating < 3
      ? '#EF4444'
      : rating < 4
        ? '#F59E0B'
        : '#10B981'

  const glowColor =
    rating < 3
      ? 'rgba(239, 68, 68, 0.3)'
      : rating < 4
        ? 'rgba(245, 158, 11, 0.3)'
        : 'rgba(16, 185, 129, 0.3)'

  return (
    <div
      ref={ref}
      className={cn('flex flex-col items-center gap-3', className)}
    >
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          className="-rotate-90"
          style={{ filter: `drop-shadow(0 0 8px ${glowColor})` }}
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="hsl(var(--muted))"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={isInView ? { strokeDashoffset: offset } : {}}
            transition={{ duration: 1.2, ease: 'easeOut', delay: 0.2 }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-3xl font-bold tabular-nums"
            style={{ color }}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.4, delay: 0.6 }}
          >
            {rating.toFixed(1)}
          </motion.span>
          <span className="text-xs text-muted-foreground">/ {maxRating}</span>
        </div>
      </div>
      <span className="text-sm font-medium text-muted-foreground">{label}</span>
    </div>
  )
}
