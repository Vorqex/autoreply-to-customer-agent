'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import { cn } from '@/lib/utils'
import {
  Search,
  Star,
  X,
  SlidersHorizontal,
  Filter,
} from 'lucide-react'

interface FiltersBarProps {
  search: string
  onSearchChange: (v: string) => void
  sentiment: string
  onSentimentChange: (v: string) => void
  platform: string
  onPlatformChange: (v: string) => void
  rating: number
  onRatingChange: (v: number) => void
  riskLevel: string
  onRiskLevelChange: (v: string) => void
  dateRange: string
  onDateRangeChange: (v: string) => void
  onClear: () => void
  hasFilters: boolean
}

const sentimentOptions = [
  { value: '', label: 'All Sentiments' },
  { value: 'positive', label: 'Positive' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'negative', label: 'Negative' },
  { value: 'very_negative', label: 'Very Negative' },
  { value: 'urgent', label: 'Urgent' },
  { value: 'spam', label: 'Spam' },
  { value: 'toxic', label: 'Toxic' },
  { value: 'fake', label: 'Fake' },
]

const platformOptions = [
  { value: '', label: 'All Platforms' },
  { value: 'google', label: 'Google' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'trustpilot', label: 'Trustpilot' },
  { value: 'yelp', label: 'Yelp' },
  { value: 'shopify', label: 'Shopify' },
  { value: 'amazon', label: 'Amazon' },
  { value: 'app_store', label: 'App Store' },
  { value: 'play_store', label: 'Play Store' },
  { value: 'airbnb', label: 'Airbnb' },
  { value: 'booking', label: 'Booking' },
]

const riskOptions = [
  { value: '', label: 'All Risk Levels' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
]

const dateRangeOptions = [
  { value: '7', label: '7d' },
  { value: '30', label: '30d' },
  { value: '90', label: '90d' },
]

export function FiltersBar({
  search,
  onSearchChange,
  sentiment,
  onSentimentChange,
  platform,
  onPlatformChange,
  rating,
  onRatingChange,
  riskLevel,
  onRiskLevelChange,
  dateRange,
  onDateRangeChange,
  onClear,
  hasFilters,
}: FiltersBarProps) {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className="relative min-w-[200px] flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              className="flex h-9 w-full rounded-xl border border-input bg-background pl-9 pr-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder="Search reviews..."
              value={search}
              onChange={(e) => onSearchChange(e.target.value)}
            />
          </div>

          <Button
            variant="outline"
            size="sm"
            className="lg:hidden"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            <SlidersHorizontal className="h-4 w-4" />
          </Button>
        </div>

        <AnimatePresence>
          {(mobileOpen || true) && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <div className="mt-3 flex flex-wrap items-center gap-3">
                <Select
                  options={sentimentOptions}
                  value={sentiment}
                  onChange={onSentimentChange}
                  placeholder="Sentiment"
                  className="min-w-[140px]"
                />

                <Select
                  options={platformOptions}
                  value={platform}
                  onChange={onPlatformChange}
                  placeholder="Platform"
                  className="min-w-[140px]"
                />

                <Select
                  options={riskOptions}
                  value={riskLevel}
                  onChange={onRiskLevelChange}
                  placeholder="Risk Level"
                  className="min-w-[140px]"
                />

                <div className="flex items-center gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => onRatingChange(star === rating ? 0 : star)}
                      className="transition-colors hover:scale-110"
                    >
                      <Star
                        className={cn(
                          'h-5 w-5',
                          star <= rating
                            ? 'fill-amber-400 text-amber-400'
                            : 'text-neutral-300 dark:text-neutral-600 hover:text-amber-300'
                        )}
                      />
                    </button>
                  ))}
                </div>

                <div className="flex items-center gap-1 rounded-lg border p-0.5">
                  {dateRangeOptions.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => onDateRangeChange(opt.value)}
                      className={cn(
                        'rounded-md px-2.5 py-1 text-xs font-medium transition-colors',
                        dateRange === opt.value
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:text-foreground'
                      )}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>

                {hasFilters && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onClear}
                    className="text-xs"
                  >
                    <X className="mr-1 h-3.5 w-3.5" />
                    Clear filters
                  </Button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  )
}
