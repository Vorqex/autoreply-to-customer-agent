'use client'

import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import type { DashboardStats, SentimentTrend, PlatformPerformance, MonthlyActivity, ApiResponse } from '@/types'

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ['analytics', 'dashboard'],
    queryFn: async () => {
      const { data } = await api.get('/analytics/dashboard')
      return data
    },
  })
}

export function useSentimentTrends(days: number = 30) {
  return useQuery<SentimentTrend[]>({
    queryKey: ['analytics', 'sentiment-trends', days],
    queryFn: async () => {
      const { data } = await api.get('/analytics/sentiment-trends', { params: { days } })
      return data
    },
  })
}

export function usePlatformPerformance() {
  return useQuery<PlatformPerformance[]>({
    queryKey: ['analytics', 'platform-performance'],
    queryFn: async () => {
      const { data } = await api.get('/analytics/platform-performance')
      return data
    },
  })
}

export function useMonthlyActivity(months: number = 12) {
  return useQuery<MonthlyActivity[]>({
    queryKey: ['analytics', 'monthly-activity', months],
    queryFn: async () => {
      const { data } = await api.get('/analytics/monthly-activity', { params: { months } })
      return data
    },
  })
}
