"use client"

import React, { useEffect, useState, useRef } from "react"
import { docsStructure } from "./sections"

export default function Sidebar() {
  const [activeId, setActiveId] = useState<string | null>(null)
  const [expandedModule, setExpandedModule] = useState<string | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)

  // evita que o IntersectionObserver sobrescreva uma seleção feita pelo usuário
  const manualSelectionUntilRef = useRef<number>(0)
  const markManualSelection = (ms = 1200) => {
    manualSelectionUntilRef.current = Date.now() + ms
  }

  // escuta eventos manuais disparados fora da Sidebar (ex: colapso na página)
  useEffect(() => {
    const handler = (e: Event) => {
      try {
        const ms = (e as CustomEvent)?.detail?.ms ?? 1200
        manualSelectionUntilRef.current = Date.now() + ms
      } catch {
        manualSelectionUntilRef.current = Date.now() + 1200
      }
    }
    window.addEventListener("docs:manualSelection", handler)
    return () => window.removeEventListener("docs:manualSelection", handler)
  }, [])

  useEffect(() => {
    const idsToObserve: string[] = []
    docsStructure.forEach((s) => {
      idsToObserve.push(s.id)
      s.subsections?.forEach((ss) => idsToObserve.push(ss.id))
    })

    const observer = new IntersectionObserver(
      (entries) => {
        // se o usuário acabou de clicar na sidebar, ignora updates do observer por um curto período
        if (Date.now() < manualSelectionUntilRef.current) return

        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id
            setActiveId(id)
            const sec = docsStructure.find((s) => s.id === id || s.subsections?.some((ss) => ss.id === id))
            if (sec) {
              setExpandedModule(sec.module)
              setExpandedSection(sec.id)
            }
          }
        })
      },
      { root: null, rootMargin: "-20% 0px -60% 0px", threshold: 0 }
    )

    idsToObserve.forEach((id) => {
      const el = document.getElementById(id)
      if (el) observer.observe(el)
    })

    return () => observer.disconnect()
  }, [])

  const modules = Array.from(new Set(docsStructure.map((s) => s.module)))

  return (
    <aside className="sticky top-6 col-span-1">
      <nav className="space-y-4 p-4 rounded-2xl bg-[var(--color-card)] border border-[var(--color-border)]">
        {modules.map((mod) => (
          <div key={mod}>
            <div
              className="flex items-center justify-between cursor-pointer"
              onClick={() => {
                // interação do usuário — marca como manual para evitar overrides do observer
                markManualSelection()
                setExpandedModule((m) => (m === mod ? null : mod))
              }}
            >
              <div className="font-semibold text-[var(--color-foreground)]">{mod}</div>
              <div className="text-sm text-[var(--color-muted)]">{expandedModule === mod ? "▾" : "▸"}</div>
            </div>

            <ul className={`mt-2 pl-3 space-y-1 ${expandedModule === mod ? "block" : "hidden"}`}>
              {docsStructure
                .filter((s) => s.module === mod)
                .map((s) => (
                  <li key={s.id}>
                    <div className="flex items-center justify-between">
                      <a
                        href={`#${s.id}`}
                        onClick={(e) => {
                          e.preventDefault()
                          // interação manual: marca e atualiza hash para abrir a seção pai
                          markManualSelection()
                          window.location.hash = s.id
                          setActiveId(s.id)
                          setExpandedSection(s.id)
                          setExpandedModule(mod)
                        }}
                        className={`block py-1 text-sm no-underline ${
                          activeId === s.id ? "font-bold text-[var(--color-accent)]" : "text-[var(--color-muted)]"
                        }`}
                      >
                        {s.title}
                      </a>

                      <button
                        className="text-xs ml-2 px-2 py-0.5 rounded bg-[var(--color-accent)] text-white"
                        onClick={() => {
                          markManualSelection()
                          setExpandedSection((cur) => (cur === s.id ? null : s.id))
                        }}
                      >
                        {expandedSection === s.id ? "▾" : "▸"}
                      </button>
                    </div>

                    <ul className={`mt-1 pl-3 space-y-1 ${expandedSection === s.id ? "block" : "hidden"}`}>
                      {s.subsections?.map((ss) => (
                        <li key={ss.id}>
                          <a
                            href={`#${ss.id}`}
                            onClick={(e) => {
                              e.preventDefault()
                              // clique em subseção: 1) abre seção pai; 2) depois atualiza hash para subseção
                              markManualSelection()
                              window.location.hash = s.id
                              setActiveId(ss.id)
                              setExpandedModule(mod)
                              setExpandedSection(s.id)

                              setTimeout(() => {
                                window.location.hash = ss.id
                              }, 60)
                            }}
                            className={`block text-sm no-underline ${
                              activeId === ss.id ? "font-bold text-[var(--color-accent)]" : "text-[var(--color-muted)]"
                            }`}
                          >
                            {ss.title}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </li>
                ))}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  )
}
