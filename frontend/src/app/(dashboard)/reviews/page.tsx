'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton, CardSkeleton } from '@/components/ui/skeleton'
import { Select } from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import { cn, formatRelativeTime, truncate, sentimentColor, riskColor } from '@/lib/utils'
import * as api from '@/lib/api'
import type { Review } from '@/types'
import {
  Search,
  Star,
  Download,
  ChevronLeft,
  ChevronRight,
  MessageSquare,
  Flag,
} from 'lucide-react'

const sentimentOptions = [
  { value: '', label: 'All Sentiments' },
  { value: 'positive', label: 'Positive' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'negative', label: 'Negative' },
  { value: 'urgent', label: 'Urgent' },
  { value: 'spam', label: 'Spam' },
]

const platformOptions = [
  { value: '', label: 'All Platforms' },
  { value: 'google', label: 'Google' },
  { value: 'facebook', label: 'Facebook' },
  { value: 'trustpilot', label: 'Trustpilot' },
  { value: 'yelp', label: 'Yelp' },
  { value: 'shopify', label: 'Shopify' },
  { value: 'amazon', label: 'Amazon' },
]

const riskOptions = [
  { value: '', label: 'All Risk Levels' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
]

const stagger = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
}

const fadeItem = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
}

export default function ReviewsPage() {
  const router = useRouter()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [sentiment, setSentiment] = useState('')
  const [platform, setPlatform] = useState('')
  const [rating, setRating] = useState(0)
  const [riskLevel, setRiskLevel] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['reviews', page, search, sentiment, platform, rating, riskLevel],
    queryFn: () =>
      api.getReviews({
        page,
        page_size: 12,
        search: search || undefined,
        sentiment: sentiment || undefined,
        platform: platform || undefined,
        rating: rating || undefined,
        risk_level: riskLevel || undefined,
      }),
  })

  const clearFilters = () => {
    setSearch('')
    setSentiment('')
    setPlatform('')
    setRating(0)
    setRiskLevel('')
    setPage(1)
  }

  const hasFilters = search || sentiment || platform || rating || riskLevel

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-bold text-foreground">Reviews</h2>
          {data && (
            <Badge variant="secondary" className="text-sm">
              {data.total}
            </Badge>
          )}
        </div>
        <Button variant="outline" size="sm">
          <Download className="mr-2 h-4 w-4" />
          Export
        </Button>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative min-w-[200px] flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                className="flex h-9 w-full rounded-xl border border-input bg-background pl-9 pr-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                placeholder="Search reviews..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1) }}
              />
            </div>

            <Select
              options={sentimentOptions}
              value={sentiment}
              onChange={(v) => { setSentiment(v); setPage(1) }}
              placeholder="Sentiment"
              className="min-w-[140px]"
            />

            <Select
              options={platformOptions}
              value={platform}
              onChange={(v) => { setPlatform(v); setPage(1) }}
              placeholder="Platform"
              className="min-w-[140px]"
            />

            <Select
              options={riskOptions}
              value={riskLevel}
              onChange={(v) => { setRiskLevel(v); setPage(1) }}
              placeholder="Risk Level"
              className="min-w-[140px]"
            />

            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => { setRating(star === rating ? 0 : star); setPage(1) }}
                  className="transition-colors"
                >
                  <Star
                    className={cn(
                      'h-5 w-5',
                      star <= rating ? 'fill-amber-400 text-amber-400' : 'text-neutral-300 dark:text-neutral-600 hover:text-amber-300'
                    )}
                  />
                </button>
              ))}
            </div>

            {hasFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                Clear filters
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : data?.items.length === 0 ? (
        <Card className="py-16 text-center">
          <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 text-lg font-semibold text-foreground">No reviews found</h3>
          <p className="mt-1 text-sm text-muted-foreground">Try adjusting your filters or connect a new platform.</p>
        </Card>
      ) : (
        <motion.div
          variants={stagger}
          initial="hidden"
          animate="show"
          className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
        >
          {data?.items.map((review) => (
            <motion.div key={review.id} variants={fadeItem}>
              <Link href={`/reviews/${review.id}`}>
                <Card
                  glass
                  className="h-full cursor-pointer transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5"
                >
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between">
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-foreground truncate">{review.customer_name}</p>
                        <p className="text-xs text-muted-foreground capitalize">{review.platform.replace('_', ' ')}</p>
                      </div>
                      <div className="flex items-center gap-1">
                        {Array.from({ length: 5 }).map((_, i) => (
                          <Star
                            key={i}
                            className={cn(
                              'h-3 w-3',
                              i < review.rating ? 'fill-amber-400 text-amber-400' : 'text-neutral-300 dark:text-neutral-600'
                            )}
                          />
                        ))}
                      </div>
                    </div>

                    <p className="mt-3 text-sm text-muted-foreground line-clamp-3">
                      {truncate(review.review_text, 120)}
                    </p>

                    <div className="mt-3 flex flex-wrap items-center gap-2">
                      <Badge className={cn('text-[10px]', sentimentColor(review.sentiment))}>
                        {review.sentiment}
                      </Badge>
                      <Badge variant="outline" className={cn('text-[10px] border', riskColor(review.risk_level))}>
                        {review.risk_level}
                      </Badge>
                      {review.is_flagged && (
                        <Badge variant="destructive" className="text-[10px]">
                          <Flag className="mr-0.5 h-2.5 w-2.5" />
                          Flagged
                        </Badge>
                      )}
                    </div>

                    {review.sentiment_confidence > 0 && (
                      <div className="mt-3">
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <span>Confidence</span>
                          <span>{Math.round(review.sentiment_confidence * 100)}%</span>
                        </div>
                        <Progress value={Math.round(review.sentiment_confidence * 100)} className="mt-1 h-1.5" />
                      </div>
                    )}

                    <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                      <span>{formatRelativeTime(review.created_at)}</span>
                      {review.reply ? (
                        <Badge variant="success" className="text-[10px]">Replied</Badge>
                      ) : (
                        <Badge variant="warning" className="text-[10px]">Pending</Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      )}

      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          {Array.from({ length: data.total_pages }, (_, i) => i + 1)
            .filter((p) => p === 1 || p === data.total_pages || Math.abs(p - page) <= 2)
            .map((p, idx, arr) => (
              <div key={p} className="flex items-center gap-1">
                {idx > 0 && arr[idx - 1] !== p - 1 && <span className="px-1 text-muted-foreground">...</span>}
                <Button
                  variant={p === page ? 'default' : 'outline'}
                  size="sm"
                  className="min-w-[36px]"
                  onClick={() => setPage(p)}
                >
                  {p}
                </Button>
              </div>
            ))}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
            disabled={page === data.total_pages}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  )
}
