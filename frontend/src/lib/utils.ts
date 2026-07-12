import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(d: string | Date) {
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(d))
}

export function formatRelativeTime(d: string | Date) {
  const now = Date.now()
  const diff = now - new Date(d).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  return `${days}d ago`
}

export function getInitials(name: string) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

export function truncate(text: string, max: number) {
  return text.length > max ? text.slice(0, max) + '...' : text
}

export function sentimentColor(s: string) {
  const map: Record<string, string> = {
    positive: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950 dark:text-emerald-400',
    neutral: 'text-amber-600 bg-amber-50 dark:bg-amber-950 dark:text-amber-400',
    negative: 'text-red-600 bg-red-50 dark:bg-red-950 dark:text-red-400',
    very_negative: 'text-red-700 bg-red-100 dark:bg-red-900 dark:text-red-300',
    urgent: 'text-orange-600 bg-orange-50 dark:bg-orange-950 dark:text-orange-400',
    spam: 'text-gray-600 bg-gray-100 dark:bg-gray-800 dark:text-gray-400',
    toxic: 'text-purple-600 bg-purple-50 dark:bg-purple-950 dark:text-purple-400',
    fake: 'text-rose-600 bg-rose-50 dark:bg-rose-950 dark:text-rose-400'
  }
  return map[s] || 'text-gray-600 bg-gray-100'
}

export function riskColor(r: string) {
  const map: Record<string, string> = {
    low: 'text-emerald-600 bg-emerald-50 border-emerald-200',
    medium: 'text-amber-600 bg-amber-50 border-amber-200',
    high: 'text-red-600 bg-red-50 border-red-200'
  }
  return map[r] || map.low
}
