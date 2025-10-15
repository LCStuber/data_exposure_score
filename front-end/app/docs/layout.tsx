"use client"

import React from 'react'
import { PropsWithChildren, useEffect, useState } from 'react'
import Link from 'next/link'
import { Sun, Moon } from 'lucide-react'

export default function DocsLayout({ children }: PropsWithChildren) {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    const root = document.documentElement
    const stored = typeof window !== 'undefined' ? localStorage.getItem('theme') : null
    if (stored === 'dark') {
      root.classList.add('dark')
      setIsDark(true)
    } else if (stored === 'light') {
      root.classList.remove('dark')
      setIsDark(false)
    } else {
      // fallback to current document state
      setIsDark(root.classList.contains('dark'))
    }
  }, [])

  const toggleTheme = () => {
    const root = document.documentElement
    if (root.classList.contains('dark')) {
      root.classList.remove('dark')
      localStorage.setItem('theme', 'light')
      setIsDark(false)
    } else {
      root.classList.add('dark')
      localStorage.setItem('theme', 'dark')
      setIsDark(true)
    }
  }

  return (
    <div className="bg-[var(--color-bg)] min-h-screen transition-colors duration-800">
      <header className="border-b border-[var(--color-border)] bg-[var(--color-card)]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <img src="/desicon.svg" alt="DES" className="w-10 h-10 rounded-md" />
            <span className="font-semibold text-lg text-[var(--color-foreground)]">DES Docs</span>
          </Link>
          <nav className="hidden md:flex gap-4 text-sm text-[var(--color-muted)] items-center">
            <Link href="/docs" className="hover:underline">Introdução</Link>
            <Link href="/docs/getting-started" className="hover:underline">Getting started</Link>
            <Link href="/docs/components" className="hover:underline">Componentes</Link>
            <button
              onClick={toggleTheme}
              aria-label="Alternar tema"
              className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-900 dark:text-slate-100"
              title="Alternar tema"
              type="button"
            >
              {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
        {children}
      </main>
    </div>
  )
}
