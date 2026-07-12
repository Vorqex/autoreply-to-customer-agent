'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { cn, formatRelativeTime, sentimentColor, riskColor } from '@/lib/utils'
import type { Review } from '@/types'
import {
  Star,
  Bot,
  Flag,
  Eye,
  ChevronDown,
  ChevronUp,
  MessageSquare,
} from 'lucide-react'

interface ReviewCardProps {
  review: Review
  onGenerate?: (id: string) => void
  onFlag?: (id: string) => void
  onView?: (id: string) => void
  loading?: boolean
}

const platformIcons: Record<string, string> = {
  google: 'G',
  facebook: 'F',
  trustpilot: 'T',
  yelp: 'Y',
  shopify: 'S',
  amazon: 'A',
  app_store: 'AS',
  play_store: 'PS',
  airbnb: 'AB',
  booking: 'B',
}

const platformColors: Record<string, string> = {
  google: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300',
  facebook: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300',
  trustpilot: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300',
  yelp: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300',
  shopify: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300',
  amazon: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300',
}

export function ReviewCard({ review, onGenerate, onFlag, onView, loading }: ReviewCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [showActions, setShowActions] = useState(false)

  const r = review
  const MAX_LENGTH = 150
  const needsTruncation = r.review_text.length > MAX_LENGTH
  const displayText = expanded ? r.review_text : r.review_text.slice(0, MAX_LENGTH)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      onHoverStart={() => setShowActions(true)}
      onHoverEnd={() => setShowActions(false)}
    >
      <Card
        glass
        className="group relative transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5"
      >
        <CardContent className="p-5">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <div
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-lg text-xs font-bold',
                  platformColors[r.platform] || 'bg-muted text-muted-foreground'
                )}
              >
                {platformIcons[r.platform] || r.platform.slice(0, 2).toUpperCase()}
              </div>
              <div>
                <p className="text-sm font-medium text-foreground">{r.customer_name}</p>
                <p className="text-xs capitalize text-muted-foreground">
                  {r.platform.replace('_', ' ')} &middot; {formatRelativeTime(r.created_at)}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-0.5">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star
                  key={i}
                  className={cn(
                    'h-3.5 w-3.5',
                    i < r.rating
                      ? 'fill-amber-400 text-amber-400'
                      : 'text-neutral-300 dark:text-neutral-600'
                  )}
                />
              ))}
            </div>
          </div>

          <div className="mt-3">
            <p className="text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap">
              {displayText}
              {!expanded && needsTruncation && '...'}
            </p>
            {needsTruncation && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="mt-1 flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-colors"
              >
                {expanded ? (
                  <>
                    Show less <ChevronUp className="h-3 w-3" />
                  </>
                ) : (
                  <>
                    Show more <ChevronDown className="h-3 w-3" />
                  </>
                )}
              </button>
            )}
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-2">
            <Badge className={cn('text-[10px]', sentimentColor(r.sentiment))}>
              {r.sentiment.replace('_', ' ')}
            </Badge>
            <Badge
              variant="outline"
              className={cn('text-[10px] border', riskColor(r.risk_level))}
            >
              {r.risk_level}
            </Badge>
            {r.needs_human_review && (
              <Badge variant="warning" className="text-[10px]">
                Needs Review
              </Badge>
            )}
          </div>

          {r.sentiment_confidence > 0 && (
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Confidence</span>
                <span>{Math.round(r.sentiment_confidence * 100)}%</span>
              </div>
              <Progress
                value={Math.round(r.sentiment_confidence * 100)}
                className="mt-1 h-1.5"
              />
            </div>
          )}

          <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
            {r.reply ? (
              <Badge variant="success" className="text-[10px]">
                <MessageSquare className="mr-0.5 h-2.5 w-2.5" />
                Replied
              </Badge>
            ) : (
              <Badge variant="warning" className="text-[10px]">
                Pending
              </Badge>
            )}
          </div>

          <motion.div
            initial={false}
            animate={{ opacity: showActions ? 1 : 0, y: showActions ? 0 : 4 }}
            transition={{ duration: 0.2 }}
            className={cn(
              'mt-3 flex items-center gap-2 border-t pt-3',
              'opacity-0 group-hover:opacity-100'
            )}
          >
            {!r.reply && (
              <Button
                size="sm"
                variant="default"
                className="h-8 text-xs"
                onClick={() => onGenerate?.(r.id)}
                disabled={loading}
              >
                <Bot className="mr-1 h-3.5 w-3.5" />
                Generate Reply
              </Button>
            )}
            <Button
              size="sm"
              variant="outline"
              className="h-8 text-xs"
              onClick={() => onView?.(r.id)}
            >
              <Eye className="mr-1 h-3.5 w-3.5" />
              View Details
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className={cn('h-8 text-xs', r.is_flagged && 'text-red-500')}
              onClick={() => onFlag?.(r.id)}
            >
              <Flag className="mr-1 h-3.5 w-3.5" />
              {r.is_flagged ? 'Flagged' : 'Flag'}
            </Button>
          </motion.div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
