"use client"

import { useEffect, useState } from 'react'

type ThemeColors = {
  border: string
  muted: string
  foreground: string
  card: string
  bg: string
  accent: string
  success: string
  warning: string
}

function readColors(): ThemeColors {
  if (typeof window === 'undefined') {
    return {
      bg: '#ffffff',
      foreground: '#0f172a',
      muted: '#475569',
      border: '#e2e8f0',
      card: '#ffffff',
      accent: '#0ea5e9',
      success: '#10b981',
      warning: '#f59e0b',
    }
  }

  const s = getComputedStyle(document.documentElement)
  const get = (name: string, fallback = '') => (s.getPropertyValue(name) || fallback).trim()

  return {
    bg: get('--color-bg', '#ffffff'),
    foreground: get('--color-foreground', '#0f172a'),
    muted: get('--color-muted', '#475569'),
    border: get('--color-border', '#e2e8f0'),
    card: get('--color-card', '#ffffff'),
    accent: get('--color-accent', '#0ea5e9'),
    success: get('--color-success', '#10b981'),
    warning: get('--color-warning', '#f59e0b'),
  }
}

export default function useThemeColors(): ThemeColors {
  const [colors, setColors] = useState<ThemeColors>(() => readColors())

  useEffect(() => {
    const update = () => setColors(readColors())
    update()
    const obs = new MutationObserver(update)
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    // also listen for theme changes via storage (in case another tab changed it)
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'theme') update()
    }
    window.addEventListener('storage', onStorage)
    return () => {
      obs.disconnect()
      window.removeEventListener('storage', onStorage)
    }
  }, [])

  return colors
}
