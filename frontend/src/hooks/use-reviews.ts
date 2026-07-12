'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import type { Review, Reply, PaginatedResponse, ApiResponse } from '@/types'

interface ReviewFilters {
  page?: number
  page_size?: number
  sentiment?: string
  platform?: string
  rating?: number
  risk_level?: string
  search?: string
  sort_by?: string
  sort_order?: string
  date_from?: string
  date_to?: string
}

export function useReviews(filters: ReviewFilters = {}) {
  return useQuery<PaginatedResponse<Review>>({
    queryKey: ['reviews', filters],
    queryFn: async () => {
      const { data } = await api.get('/reviews', { params: filters })
      return data
    },
  })
}

export function useReview(id: string) {
  return useQuery<Review>({
    queryKey: ['review', id],
    queryFn: async () => {
      const { data } = await api.get(`/reviews/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useGenerateReply() {
  const queryClient = useQueryClient()
  return useMutation<Reply, Error, string>({
    mutationFn: async (reviewId: string) => {
      const { data } = await api.post(`/reviews/${reviewId}/generate-reply`)
      return data
    },
    onSuccess: (_data, reviewId) => {
      queryClient.invalidateQueries({ queryKey: ['review', reviewId] })
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export function useApproveReply() {
  const queryClient = useQueryClient()
  return useMutation<Reply, Error, string>({
    mutationFn: async (reviewId: string) => {
      const { data } = await api.post(`/reviews/${reviewId}/approve-reply`)
      return data
    },
    onSuccess: (_data, reviewId) => {
      queryClient.invalidateQueries({ queryKey: ['review', reviewId] })
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export function useRejectReply() {
  const queryClient = useQueryClient()
  return useMutation<Reply, Error, string>({
    mutationFn: async (reviewId: string) => {
      const { data } = await api.post(`/reviews/${reviewId}/reject-reply`)
      return data
    },
    onSuccess: (_data, reviewId) => {
      queryClient.invalidateQueries({ queryKey: ['review', reviewId] })
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export function usePublishReply() {
  const queryClient = useQueryClient()
  return useMutation<Reply, Error, string>({
    mutationFn: async (reviewId: string) => {
      const { data } = await api.post(`/reviews/${reviewId}/publish-reply`)
      return data
    },
    onSuccess: (_data, reviewId) => {
      queryClient.invalidateQueries({ queryKey: ['review', reviewId] })
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export function useRegenerateReply() {
  const queryClient = useQueryClient()
  return useMutation<Reply, Error, string>({
    mutationFn: async (reviewId: string) => {
      const { data } = await api.post(`/reviews/${reviewId}/regenerate-reply`)
      return data
    },
    onSuccess: (_data, reviewId) => {
      queryClient.invalidateQueries({ queryKey: ['review', reviewId] })
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export function useFlagReview() {
  const queryClient = useQueryClient()
  return useMutation<Review, Error, { reviewId: string; reason?: string }>({
    mutationFn: async ({ reviewId, reason }) => {
      const { data } = await api.patch(`/reviews/${reviewId}/flag`, { reason })
      return data
    },
    onSuccess: (_data, { reviewId }) => {
      queryClient.invalidateQueries({ queryKey: ['review', reviewId] })
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}
