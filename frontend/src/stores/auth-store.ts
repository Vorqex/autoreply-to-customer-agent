'use client'

import { create } from 'zustand'
import type { User } from '@/types'
import { getToken, setToken, setRefreshToken, removeToken, removeRefreshToken, isAuthenticated } from '@/lib/auth'
import * as api from '@/lib/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async (email: string, password: string) => {
    const res = await api.login(email, password)
    setToken(res.access_token)
    setRefreshToken(res.refresh_token)
    set({ user: res.user, isAuthenticated: true, isLoading: false })
  },
  logout: () => {
    removeToken()
    removeRefreshToken()
    set({ user: null, isAuthenticated: false, isLoading: false })
  },
  checkAuth: async () => {
    if (!isAuthenticated()) {
      set({ user: null, isAuthenticated: false, isLoading: false })
      return
    }
    try {
      const user = await api.getMe()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch {
      removeToken()
      removeRefreshToken()
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },
}))
