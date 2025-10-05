"use client"
import { useEffect, useState } from 'react'
import { Sun, Moon } from 'lucide-react'

export default function ThemeToggle() {
  const [mounted, setMounted] = useState(false)
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    setMounted(true)
    const root = document.documentElement
    setIsDark(root.classList.contains('dark'))
  }, [])

  const toggle = () => {
    const root = document.documentElement
    if (isDark) {
      root.classList.remove('dark')
      localStorage.setItem('theme', 'light')
      setIsDark(false)
    } else {
      root.classList.add('dark')
      localStorage.setItem('theme', 'dark')
      setIsDark(true)
    }
  }

  if (!mounted) return null

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label="Alternar tema"
      title="Alternar tema"
      className="fixed bottom-4 right-4 z-50 p-3 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 shadow hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
    >
      {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </button>
  )
}