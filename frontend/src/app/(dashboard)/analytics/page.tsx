'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { StatsCard } from '@/components/analytics/stats-card'
import { SentimentChart } from '@/components/analytics/sentiment-chart'
import { ActivityChart } from '@/components/analytics/activity-chart'
import { RatingRing } from '@/components/analytics/rating-ring'
import { cn } from '@/lib/utils'
import { useDashboardStats, useSentimentTrends, usePlatformPerformance, useMonthlyActivity } from '@/hooks/use-analytics'
import {
  TrendingUp,
  TrendingDown,
  Bot,
  Edit3,
  Clock,
  CheckCircle,
  Download,
  FileText,
  BarChart3,
  Star,
} from 'lucide-react'

type DateRange = '7' | '30' | '90' | 'custom'

const dateRangeOptions: { value: DateRange; label: string }[] = [
  { value: '7', label: 'Last 7 days' },
  { value: '30', label: 'Last 30 days' },
  { value: '90', label: 'Last 90 days' },
  { value: 'custom', label: 'Custom' },
]

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
}

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
}

const complaintData = [
  { phrase: 'Slow service', count: 42 },
  { phrase: 'Too expensive', count: 38 },
  { phrase: 'Wrong order', count: 29 },
  { phrase: 'Rude staff', count: 24 },
  { phrase: 'Quality issues', count: 21 },
  { phrase: 'Long wait time', count: 18 },
  { phrase: 'Not as described', count: 15 },
  { phrase: 'Difficult to contact', count: 12 },
]

const topTemplates = [
  { name: 'Thank You - Positive Review', usage: 245, success_rate: 94 },
  { name: 'Apology - Negative Review', usage: 178, success_rate: 88 },
  { name: 'Follow-up - Neutral Review', usage: 134, success_rate: 82 },
  { name: 'Resolution - Complaint', usage: 98, success_rate: 91 },
  { name: 'Welcome - New Customer', usage: 76, success_rate: 96 },
]

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState<DateRange>('30')
  const days = dateRange === 'custom' ? 30 : parseInt(dateRange)

  const { data: stats, isLoading: statsLoading } = useDashboardStats()
  const { data: sentimentData, isLoading: sentimentLoading } = useSentimentTrends(days)
  const { data: platformData, isLoading: platformLoading } = usePlatformPerformance()
  const { data: activityData, isLoading: activityLoading } = useMonthlyActivity()

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item} className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Analytics</h2>
          <p className="text-sm text-muted-foreground">Track performance and trends across all platforms</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 rounded-xl border p-1">
            {dateRangeOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setDateRange(opt.value)}
                className={cn(
                  'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                  dateRange === opt.value
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {opt.label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-1">
            <Button variant="outline" size="sm">
              <FileText className="mr-1.5 h-4 w-4" />
              PDF
            </Button>
            <Button variant="outline" size="sm">
              <Download className="mr-1.5 h-4 w-4" />
              CSV
            </Button>
          </div>
        </div>
      </motion.div>

      <motion.div variants={item} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="AI Reply Acceptance"
          value={statsLoading ? 0 : 87}
          trend="positive"
          trendLabel="+5.2%"
          icon={<CheckCircle className="h-5 w-5" />}
          loading={statsLoading}
          format="percentage"
        />
        <StatsCard
          title="Human Edit Rate"
          value={statsLoading ? 0 : 23}
          trend="negative"
          trendLabel="-2.1%"
          icon={<Edit3 className="h-5 w-5" />}
          loading={statsLoading}
          format="percentage"
        />
        <StatsCard
          title="Avg Quality Score"
          value={statsLoading ? 0 : 91}
          trend="positive"
          trendLabel="+1.8%"
          icon={<Star className="h-5 w-5" />}
          loading={statsLoading}
          format="percentage"
        />
        <StatsCard
          title="Avg Response Time"
          value={statsLoading ? 0 : 4.2}
          trend="positive"
          trendLabel="-12%"
          icon={<Clock className="h-5 w-5" />}
          loading={statsLoading}
          format="duration"
        />
      </motion.div>

      <motion.div variants={item} className="grid gap-6 lg:grid-cols-3">
        <Card glass className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-primary" />
              Sentiment Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SentimentChart data={sentimentData || []} loading={sentimentLoading} />
          </CardContent>
        </Card>

        <Card glass>
          <CardHeader>
            <CardTitle className="text-base">Platform Performance</CardTitle>
          </CardHeader>
          <CardContent>
            {platformLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full rounded-xl" />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {(platformData || []).map((p) => (
                  <div
                    key={p.platform}
                    className="flex items-center justify-between rounded-xl border p-3 text-sm transition-colors hover:bg-accent/50"
                  >
                    <div className="flex items-center gap-2">
                      <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-xs font-bold text-primary">
                        {p.platform.slice(0, 2).toUpperCase()}
                      </div>
                      <span className="capitalize font-medium text-foreground">
                        {p.platform.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1 text-xs">
                        <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                        <span>{p.avg_rating.toFixed(1)}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">{p.total} reviews</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={item} className="grid gap-6 lg:grid-cols-2">
        <Card glass>
          <CardHeader>
            <CardTitle className="text-base">Most Common Complaints</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={complaintData} layout="vertical" barCategoryGap="20%">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="phrase"
                  tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
                  tickLine={false}
                  axisLine={false}
                  width={140}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '12px',
                  }}
                  cursor={{ fill: 'hsl(var(--muted) / 0.3)' }}
                />
                <Bar dataKey="count" fill="#EF4444" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card glass>
          <CardHeader>
            <CardTitle className="text-base">Top Performing Templates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-hidden rounded-xl border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-3 text-left font-medium text-muted-foreground">Template</th>
                    <th className="px-4 py-3 text-right font-medium text-muted-foreground">Usage</th>
                    <th className="px-4 py-3 text-right font-medium text-muted-foreground">Success</th>
                  </tr>
                </thead>
                <tbody>
                  {topTemplates.map((t, i) => (
                    <tr key={i} className="border-b last:border-0 hover:bg-accent/30 transition-colors">
                      <td className="px-4 py-3 text-foreground font-medium">{t.name}</td>
                      <td className="px-4 py-3 text-right text-muted-foreground">{t.usage}</td>
                      <td className="px-4 py-3 text-right">
                        <Badge
                          variant={t.success_rate >= 90 ? 'success' : t.success_rate >= 80 ? 'warning' : 'destructive'}
                          className="text-[10px]"
                        >
                          {t.success_rate}%
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={item} className="grid gap-6 lg:grid-cols-2">
        <Card glass>
          <CardHeader>
            <CardTitle className="text-base">Monthly Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <ActivityChart data={activityData || []} loading={activityLoading} />
          </CardContent>
        </Card>

        <Card glass>
          <CardHeader>
            <CardTitle className="text-base">Average Rating</CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center py-6">
            <RatingRing rating={stats?.avg_rating ?? 4.2} label="Across all platforms" />
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
