'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import type { BrandVoice } from '@/types'

export function useBrandVoice() {
  return useQuery<BrandVoice>({
    queryKey: ['brand-voice'],
    queryFn: async () => {
      const { data } = await api.get('/brand-voice')
      return data
    },
  })
}

export function useUpdateBrandVoice() {
  const queryClient = useQueryClient()
  return useMutation<BrandVoice, Error, Partial<BrandVoice>>({
    mutationFn: async (payload) => {
      const { data } = await api.patch('/brand-voice', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brand-voice'] })
    },
  })
}
