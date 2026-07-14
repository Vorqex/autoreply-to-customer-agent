'use client'

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { cn } from '@/lib/utils'
import type { MonthlyActivity } from '@/types'

interface ActivityChartProps {
  data: MonthlyActivity[]
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

export function ActivityChart({ data, loading, className }: ActivityChartProps) {
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
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="reviewsGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#0EA5E9" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#0EA5E9" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="repliesGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="aiGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
          <XAxis
            dataKey="month"
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
          <Area
            type="monotone"
            dataKey="reviews"
            name="Reviews"
            stroke="#0EA5E9"
            strokeWidth={2}
            fill="url(#reviewsGrad)"
          />
          <Area
            type="monotone"
            dataKey="replies"
            name="Replies"
            stroke="#10B981"
            strokeWidth={2}
            fill="url(#repliesGrad)"
          />
          <Area
            type="monotone"
            dataKey="ai_generations"
            name="AI Generations"
            stroke="#F59E0B"
            strokeWidth={2}
            fill="url(#aiGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
