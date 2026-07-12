'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { cn } from '@/lib/utils'
import type { SentimentTrend } from '@/types'

interface SentimentChartProps {
  data: SentimentTrend[]
  loading?: boolean
  className?: string
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-xl border bg-card/95 backdrop-blur-sm p-3 shadow-xl text-xs">
      <p className="mb-2 font-medium text-foreground">{label}</p>
      {payload.map((entry: any) => (
        <div key={entry.name} className="flex items-center gap-2 py-0.5">
          <span
            className="h-2.5 w-2.5 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="capitalize text-muted-foreground">{entry.name.replace('_', ' ')}</span>
          <span className="ml-auto font-medium text-foreground">{entry.value}</span>
        </div>
      ))}
    </div>
  )
}

export function SentimentChart({ data, loading, className }: SentimentChartProps) {
  if (loading) {
    return (
      <div className={cn('flex h-[300px] items-center justify-center', className)}>
        <div className="h-[280px] w-full animate-pulse rounded-xl bg-muted" />
      </div>
    )
  }

  if (!data?.length) {
    return (
      <div className={cn('flex h-[300px] items-center justify-center text-sm text-muted-foreground', className)}>
        No data available
      </div>
    )
  }

  return (
    <div className={cn('w-full', className)}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} barGap={2} barCategoryGap="20%">
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
            tickLine={false}
            axisLine={false}
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'hsl(var(--muted) / 0.3)' }} />
          <Legend
            wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
            iconType="circle"
            iconSize={8}
          />
          <Bar
            dataKey="positive"
            name="Positive"
            fill="#10B981"
            radius={[4, 4, 0, 0]}
            stackId="sentiment"
          />
          <Bar
            dataKey="neutral"
            name="Neutral"
            fill="#F59E0B"
            radius={[4, 4, 0, 0]}
            stackId="sentiment"
          />
          <Bar
            dataKey="negative"
            name="Negative"
            fill="#EF4444"
            radius={[4, 4, 0, 0]}
            stackId="sentiment"
          />
          <Bar
            dataKey="very_negative"
            name="Very Negative"
            fill="#991B1B"
            radius={[4, 4, 0, 0]}
            stackId="sentiment"
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
