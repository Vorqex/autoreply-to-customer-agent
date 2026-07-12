'use client'

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton, CardSkeleton } from '@/components/ui/skeleton'
import { cn, formatRelativeTime, truncate, sentimentColor } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth-store'
import * as api from '@/lib/api'
import {
  Inbox,
  Clock,
  Bot,
  Edit3,
  TrendingUp,
  TrendingDown,
  Star,
  ExternalLink,
} from 'lucide-react'

const statCards = [
  { key: 'total_reviews', label: 'Total Reviews', icon: Inbox, color: 'text-indigo-600 bg-indigo-100 dark:bg-indigo-950 dark:text-indigo-400' },
  { key: 'pending_replies', label: 'Pending Replies', icon: Clock, color: 'text-amber-600 bg-amber-100 dark:bg-amber-950 dark:text-amber-400' },
  { key: 'auto_replied', label: 'Auto-Replied', icon: Bot, color: 'text-emerald-600 bg-emerald-100 dark:bg-emerald-950 dark:text-emerald-400' },
  { key: 'manual_replies', label: 'Manual Replies', icon: Edit3, color: 'text-blue-600 bg-blue-100 dark:bg-blue-950 dark:text-blue-400' },
]

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08 },
  },
}

const statItem = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
}

const platforms = [
  { name: 'Google', connected: true },
  { name: 'Facebook', connected: true },
  { name: 'Trustpilot', connected: true },
  { name: 'Yelp', connected: true },
  { name: 'Shopify', connected: false },
  { name: 'Amazon', connected: false },
]

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: api.getDashboardStats,
  })

  const { data: sentimentTrends } = useQuery({
    queryKey: ['sentiment-trends'],
    queryFn: api.getSentimentTrends,
  })

  const { data: monthlyActivity } = useQuery({
    queryKey: ['monthly-activity'],
    queryFn: api.getMonthlyActivity,
  })

  const { data: reviewsData } = useQuery({
    queryKey: ['recent-reviews'],
    queryFn: () => api.getReviews({ page: 1, page_size: 5, sort_by: 'created_at', sort_order: 'desc' }),
  })

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={statItem}>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-foreground">
              {greeting}, {user?.full_name?.split(' ')[0] || 'there'}
            </h2>
            <p className="text-sm text-muted-foreground">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
            </p>
          </div>
        </div>
      </motion.div>

      <motion.div variants={statItem} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => {
          const Icon = card.icon
          const value = stats?.[card.key as keyof typeof stats]
          return (
            <Card key={card.key} glass className="transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className={cn('rounded-xl p-2.5', card.color)}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {statsLoading ? '...' : '+12%'}
                  </Badge>
                </div>
                <div className="mt-4">
                  {statsLoading ? (
                    <Skeleton className="h-8 w-20" />
                  ) : (
                    <p className="text-3xl font-bold text-foreground">{value ?? 0}</p>
                  )}
                  <p className="mt-1 text-sm text-muted-foreground">{card.label}</p>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </motion.div>

      <motion.div variants={statItem} className="grid gap-6 lg:grid-cols-2">
        <Card glass>
          <CardHeader>
            <CardTitle className="text-base">Sentiment Trends</CardTitle>
          </CardHeader>
          <CardContent>
            {sentimentTrends ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={sentimentTrends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                  <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '12px',
                    }}
                  />
                  <Bar dataKey="positive" fill="#10B981" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="neutral" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="negative" fill="#EF4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Skeleton className="h-[280px] w-full" />
            )}
          </CardContent>
        </Card>

        <Card glass>
          <CardHeader>
            <CardTitle className="text-base">Monthly Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {monthlyActivity ? (
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={monthlyActivity}>
                  <defs>
                    <linearGradient id="reviewsGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="repliesGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                  <YAxis tick={{ fontSize: 12 }} stroke="hsl(var(--muted-foreground))" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '12px',
                    }}
                  />
                  <Area type="monotone" dataKey="reviews" stroke="#6366F1" fill="url(#reviewsGrad)" strokeWidth={2} />
                  <Area type="monotone" dataKey="replies" stroke="#10B981" fill="url(#repliesGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <Skeleton className="h-[280px] w-full" />
            )}
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={statItem} className="grid gap-6 lg:grid-cols-2">
        <Card glass>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Recent Reviews</CardTitle>
            <Badge variant="outline" className="cursor-pointer">View all</Badge>
          </CardHeader>
          <CardContent className="space-y-3">
            {reviewsData?.items ? (
              reviewsData.items.slice(0, 5).map((review) => (
                <div
                  key={review.id}
                  className="flex items-start justify-between rounded-xl border p-3 transition-colors hover:bg-accent/50"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-foreground">{review.customer_name}</span>
                      <div className="flex items-center gap-0.5">
                        {Array.from({ length: 5 }).map((_, i) => (
                          <Star
                            key={i}
                            className={cn('h-3 w-3', i < review.rating ? 'fill-amber-400 text-amber-400' : 'text-neutral-300 dark:text-neutral-600')}
                          />
                        ))}
                      </div>
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground line-clamp-1">
                      {truncate(review.review_text, 80)}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">{formatRelativeTime(review.created_at)}</p>
                  </div>
                  <Badge className={cn('ml-3 shrink-0', sentimentColor(review.sentiment))}>
                    {review.sentiment}
                  </Badge>
                </div>
              ))
            ) : (
              Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full rounded-xl" />
              ))
            )}
          </CardContent>
        </Card>

        <Card glass>
          <CardHeader>
            <CardTitle className="text-base">Connected Platforms</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3">
            {platforms.map((p) => (
              <div
                key={p.name}
                className={cn(
                  'flex items-center gap-3 rounded-xl border p-3 transition-all',
                  p.connected
                    ? 'border-emerald-200 bg-emerald-50/50 dark:border-emerald-900 dark:bg-emerald-950/20'
                    : 'border-neutral-200 opacity-50 dark:border-neutral-700'
                )}
              >
                <div
                  className={cn(
                    'h-2.5 w-2.5 rounded-full',
                    p.connected ? 'bg-emerald-500 shadow-lg shadow-emerald-500/30' : 'bg-neutral-300'
                  )}
                />
                <span className="text-sm font-medium text-foreground">{p.name}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
