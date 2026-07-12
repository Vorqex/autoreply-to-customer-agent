'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/lib/api'
import type { BrandVoice } from '@/types'

export function useBrandVoice() {
  return useQuery<BrandVoice>({
    queryKey: ['brand-voice'],
    queryFn: () => api.getBrandVoice(),
  })
}

export function useUpdateBrandVoice() {
  const queryClient = useQueryClient()
  return useMutation<BrandVoice, Error, Partial<BrandVoice>>({
    mutationFn: (payload) => api.updateBrandVoice(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brand-voice'] })
    },
  })
}


