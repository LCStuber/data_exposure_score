"use client"

import React, { useState, useEffect, useRef } from "react"
import Sidebar from "./Sidebar"
import { docsStructure } from "./sections"

// novos imports de conteúdo
import IntroOverview from "./contents/intro-overview"
import IntroSignificado from "./contents/intro-significado"
import MethodCollection from "./contents/method-collection"
import MethodAnalysis from "./contents/method-analysis"
import IntroObjetivos from "./contents/intro-objetivos"


const contentMap: Record<string, React.FC> = {
  "intro-overview": IntroOverview,
  "intro-significado": IntroSignificado,
  "intro-objetivos": IntroObjetivos,
  "method-collection": MethodCollection,
  "method-analysis": MethodAnalysis,
}

function CollapsibleSection({
  id,
  title,
  defaultOpen = false,
  children,
}: {
  id: string
  title: string
  defaultOpen?: boolean
  children: React.ReactNode
}) {
  const [open, setOpen] = useState(defaultOpen)
  const rootRef = useRef<HTMLElement | null>(null)

  // envia um evento para informar a Sidebar que houve interação manual
  const markManualSelection = (ms = 1200) => {
    try {
      window.dispatchEvent(new CustomEvent("docs:manualSelection", { detail: { ms } }))
    } catch {
      // noop - ambiente sem window
    }
  }

  useEffect(() => {
    function openIfHashTargetsMe() {
      const hash = window.location.hash.replace(/^#/, "")
      if (!hash) return

      // se o hash for a própria seção
      if (hash === id) {
        setOpen(true)
        const el = document.getElementById(id)
        el?.scrollIntoView({ behavior: "smooth", block: "start" })
        return
      }

      // se o hash for uma subseção que esteja dentro desta seção
      const target = document.getElementById(hash)
      if (target && rootRef.current?.contains(target)) {
        setOpen(true)
        target.scrollIntoView({ behavior: "smooth", block: "start" })
      }
    }

    // checar no mount (caso o link já venha com hash) e quando o hash mudar
    openIfHashTargetsMe()
    window.addEventListener("hashchange", openIfHashTargetsMe)
    return () => window.removeEventListener("hashchange", openIfHashTargetsMe)
  }, [id])

  return (
    <section id={id} ref={rootRef} className="space-y-4">
      {/* Cabeçalho: pequeno quadrado com o título */}
      <div
        className="flex items-center gap-4 cursor-pointer"
        onClick={() => {
          markManualSelection()
          setOpen((s) => !s)
        }}
      >
        <div className="ml-2 my-2 flex-1">
          <div className="flex items-center justify-between">
            <a
              href={`#${id}`}
              className="text-2xl font-bold text-[var(--color-foreground)] no-underline"
            >
              {title}
            </a>

            <button
              aria-expanded={open}
              className="ml-4 text-sm px-3 py-1 rounded-md bg-[var(--color-muted)] text-[var(--color-foreground)]"
              onClick={(e) => {
                e.stopPropagation()
                markManualSelection()
                setOpen((s) => !s)
              }}
            >
              {open ? "Ocultar" : "Mostrar"}
            </button>
          </div>

          {/* resumo opcional da seção macro */}
          {/* <p className="mt-2 text-sm text-[var(--color-muted)]">Resumo da seção {title}.</p> */}
        </div>
      </div>

      {/* Conteúdo das subseções como blocos separados */}
      {open && <div className="grid gap-4">{children}</div>}
    </section>
  )
}

function SubSection({ id, title, children }: { id: string; title: string; children?: React.ReactNode }) {
  // Subseção NÃO colapsável — sempre exibe o conteúdo
  return (
    <article id={id} className="rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-4 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h4 className="text-2xl ml-2 font-semibold">{title}</h4>
          <p className="mt-1 text-sm text-[var(--color-muted)]">{/* descrição curta opcional */}</p>
        </div>
      </div>

      <div className="mt-3 text-sm text-[var(--color-muted)]">{children}</div>
    </article>
  )
}

export default function DocsPage() {
  return (
    <>
      <Sidebar />
      <article className="lg:col-span-3 space-y-6">
        {docsStructure.map((section) => (
          <CollapsibleSection
            key={section.id}
            id={section.id}
            title={section.title}
            defaultOpen={section.id === "introduction"}
          >
            {/* subseções como blocos separados */}
            {section.subsections?.map((ss) => {
              const Content = contentMap[ss.id] ?? (() => <></>)
              return (
                <SubSection key={ss.id} id={ss.id} title={ss.title}>
                  <Content />
                </SubSection>
              )
            })}
          </CollapsibleSection>
        ))}
      </article>
    </>
  )
}