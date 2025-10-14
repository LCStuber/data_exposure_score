import React from 'react'
import Link from 'next/link'

export default function Sidebar() {
  const sections = [
    { id: 'introduction', title: 'Introdução' },
    { id: 'methodology', title: 'Metodologia' },
    // { id: 'installation', title: 'Instalação' },
    // { id: 'usage', title: 'Uso Rápido' },
    // { id: 'components', title: 'Componentes' },
    // { id: 'theming', title: 'Theming' },
  ]

  return (
    <aside className="lg:col-span-1 bg-[var(--color-card)] border border-[var(--color-border)] rounded-2xl p-5 shadow-sm sticky top-24 h-fit">
      <h4 className="text-lg font-semibold text-[var(--color-muted)] mb-3">Navegação</h4>
      <nav className="flex flex-col gap-2 text-sm text-[var(--color-foreground)]">
        {sections.map((s) => (
          <a key={s.id} href={`#${s.id}`} className="py-2 px-3 rounded hover:bg-[var(--color-muted)]">{s.title}</a>
        ))}
      </nav>
      <div className="mt-4 border-t border-[var(--color-border)] pt-4 text-xs text-[var(--color-muted)]">
        <div>Versão da docs: 1.0</div>
        <Link href="/" className="text-[var(--color-accent)] hover:underline">Voltar a home</Link>
      </div>
    </aside>
  )
}
