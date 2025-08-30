  'use client'

  import Link from 'next/link'
  import Image from 'next/image'
  import { useEffect, useMemo, useRef, useState } from 'react'
  import {
    Search,
    Sun,
    Github,
    Menu,
    Users,
    BarChart2,
    TrendingUp,
    ShieldCheck,
    Database,
  } from 'lucide-react'
  import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    CartesianGrid,
  } from 'recharts'

  // ----------------- Types & Mock helpers -----------------
  type Gender = 'male' | 'female' | 'other'
  type User = { id: string; age: number; gender: Gender; score: number }

  const rand = (min: number, max: number) =>
    Math.floor(Math.random() * (max - min + 1)) + min

  function generateMockUsers(n = 360): User[] {
    const genders: Gender[] = ['male', 'female', 'other']
    return Array.from({ length: n }).map((_, i) => {
      const base = rand(320, 920)
      const monthly = Array.from({ length: 12 }).map((m) =>
        Math.max(
          0,
          Math.min(
            1000,
            Math.round(
              base +
                Math.sin((m / 12) * Math.PI * 2) * rand(0, 30) +
                rand(-35, 35)
            )
          )
        )
      )
      return {
        id: `user_${i + 1}`,
        age: rand(14, 75),
        gender: genders[Math.floor(Math.random() * genders.length)],
        score: base,
      }
    })
  }
  const avg = (arr: number[]) =>
    arr.length ? arr.reduce((s, v) => s + v, 0) / arr.length : 0
  const bucketsFor = (scores: number[], size = 200) => {
    const b = Array.from({ length: Math.ceil(1000 / size) }, () => 0)
    scores.forEach((s) => b[Math.min(b.length - 1, Math.floor(s / size))]++)
    return b
  }

  // ----------------- UI: Navbar -----------------
  function NavBar() {
    const [open, setOpen] = useState(false)
    const searchRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
      const onKey = (e: KeyboardEvent) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
          e.preventDefault()
          searchRef.current?.focus()
        }
      }
      window.addEventListener('keydown', onKey)
      return () => window.removeEventListener('keydown', onKey)
    }, [])

    return (
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur supports-[backdrop-filter]:bg-white/70">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="h-16 flex items-center justify-between">
            {/* esquerda: logo + links */}
            <div className="flex items-center gap-5">
              <Link href="#" className="flex items-center gap-2">
                <span className="font-semibold text-lg tracking-tight text-black">
                  DES Dashboard
                </span>
              </Link>

              <nav className="hidden md:flex items-center gap-5 text-sm text-slate-600">
                <a href="#overview" className="hover:text-slate-900">Visão Geral</a>
                <a href="#charts" className="hover:text-slate-900">Gráficos</a>
                <a href="#users" className="hover:text-slate-900">Usuários</a>
                <a href="#docs" className="hover:text-slate-900">Docs</a>
              </nav>
            </div>

            {/* direita: busca + ícones + CTA */}
            <div className="flex items-center gap-2">
              <div className="relative hidden sm:block">
                <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  ref={searchRef}
                  placeholder="Buscar…"
                  aria-label="Buscar"
                  className="pl-8 pr-14 py-2 rounded-lg bg-white ring-1 ring-slate-200 placeholder:text-slate-400 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 w-56 shadow-sm"
                />
                <kbd className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-slate-500 border border-slate-300 rounded px-1 bg-slate-50">
                  Ctrl K
                </kbd>
              </div>

              <button
                aria-label="Alternar tema"
                className="p-2 rounded-xl hover:bg-slate-100"
                title="Alternar tema"
                type="button"
              >
                <Sun className="h-5 w-5" />
              </button>

              <a
                href="https://github.com/"
                target="_blank"
                className="p-2 rounded-xl hover:bg-slate-100"
                aria-label="GitHub"
                rel="noreferrer"
              >
                <Github className="h-5 w-5" />
              </a>
              <button
                className="md:hidden p-2 rounded-xl hover:bg-slate-100"
                onClick={() => setOpen((v) => !v)}
                aria-label="Abrir menu"
                type="button"
              >
                <Menu className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>

        {/* menu mobile */}
        {open && (
          <div className="md:hidden border-t border-slate-200 bg-white">
            <nav className="px-4 py-3 flex flex-col gap-2 text-sm text-slate-700">
              <a href="#overview" className="hover:text-slate-900" onClick={() => setOpen(false)}>Visão Geral</a>
              <a href="#charts" className="hover:text-slate-900" onClick={() => setOpen(false)}>Gráficos</a>
              <a href="#users" className="hover:text-slate-900" onClick={() => setOpen(false)}>Usuários</a>
            </nav>
          </div>
        )}
      </header>
    )
  }

  // ----------------- Page -----------------

const ageRanges = [
  { label: 'Todos', min: 0, max: 999 },
  { label: '< 18', min: 0, max: 17 },
  { label: '18-24', min: 18, max: 24 },
  { label: '25-34', min: 25, max: 34 },
  { label: '35-44', min: 35, max: 44 },
  { label: '45-54', min: 45, max: 54 },
  { label: '55-64', min: 55, max: 64 },
  { label: '65+', min: 65, max: 999 },
]

export default function Page() {
  const [users] = useState<User[]>(() => generateMockUsers(360))

  const [isZoomed, setIsZoomed] = useState(false);
  const [selectedAgeRange, setSelectedAgeRange] = useState(ageRanges[0])
  const [genderFilter, setGenderFilter] = useState({
    male: true,
    female: true,
    other: true,
  })

  const toggleGender = (k: keyof typeof genderFilter) =>
    setGenderFilter((s) => ({ ...s, [k]: !s[k] }))

  const clearFilters = () => {
    setSelectedAgeRange(ageRanges[0])
    setGenderFilter({ male: true, female: true, other: true })
  }

  const allowed = useMemo(() => {
    const arr: Gender[] = []
    if (genderFilter.male) arr.push('male')
    if (genderFilter.female) arr.push('female')
    if (genderFilter.other) arr.push('other')
    return arr
  }, [genderFilter])

  const filtered = useMemo(
    () =>
      users.filter(
        (u) =>
          u.age >= selectedAgeRange.min &&
          u.age <= selectedAgeRange.max &&
          allowed.includes(u.gender)
      ),
    [users, selectedAgeRange, allowed]
  )

  const scores = useMemo(() => filtered.map((u) => u.score), [filtered])
  const kAvgScore = Math.round(avg(scores) || 0)
  const kPct800 = filtered.length
    ? Math.round(
        (filtered.filter((u) => u.score >= 800).length / filtered.length) * 100
      )
    : 0
  const kCount = filtered.length
  const signal = kAvgScore >= 700 ? 'Seguro' : kAvgScore >= 500 ? 'Moderado' : 'Alto'

  const distBuckets = useMemo(() => bucketsFor(scores, 200), [scores])
  const distData = distBuckets.map((v, i) => ({
    label: i === distBuckets.length - 1 ? '800–1000' : `${i * 200}–${i * 200 + 199}`,
    value: v,
  }))
  
  // --- NOVA LÓGICA PARA SIMULAR A SÉRIE TEMPORAL ---
  const series = useMemo(() => {
    // Se não houver usuários, retorna um array vazio
    if (filtered.length === 0) {
      return Array.from({ length: 12 }).map((_, m) => ({ month: `${m + 1}`, value: 0 }));
    }

    // 1. Calcula a média do grupo como linha de base
    const baselineAvg = avg(scores);
    // 2. Define uma variação (ex: 5% da média) para a curva não ser reta
    const amplitude = baselineAvg * 0.05;

    // 3. Gera 12 pontos de dados usando uma onda senoidal + aleatoriedade
    return Array.from({ length: 12 }).map((_, m) => ({
      month: `${m + 1}`,
      value: Math.round(
        Math.max(0, Math.min(1000, // Garante que o valor fique entre 0 e 1000
          baselineAvg +
          Math.sin((m / 11) * Math.PI * 2) * amplitude + // Cria a onda suave
          rand(-20, 20) // Adiciona um pouco de ruído para parecer mais real
        ))
      )
    }));
  }, [filtered, scores]); // Recalcula a tendência sempre que os filtros mudam

  return (
    <div className="bg-slate-50 min-h-screen">
      <NavBar />

      <section id="overview" className="border-b border-slate-200 bg-gradient-to-br from-white to-slate-50">
        <div className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 ">DES Dashboard</h1>
            <p className="text-sm md:text-base text-slate-600 mt-1">Índice de Exposição Digital — Bluesky (dados de exemplo)</p>
          </div>
          <button className="px-3 py-2 rounded-xl bg-sky-600 text-white hover:bg-sky-700 text-sm shadow-sm">Exportar</button>
        </div>
      </section>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-4 gap-6" id="charts">
        <aside className="lg:col-span-1 bg-white border rounded-2xl p-5 shadow-sm sticky top-24 h-fit">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-500">Filtros</h3>
            <button onClick={clearFilters} className="text-sm text-sky-700 hover:underline" type="button">
              Limpar
            </button>
          </div>

          <label className="block text-sm font-medium text-slate-700 mb-2">Idade</label>
          <div className="flex flex-wrap gap-2">
            {ageRanges.map((range) => (
              <button key={range.label} onClick={() => setSelectedAgeRange(range)} type="button" className={`px-3 py-1.5 rounded-full text-sm border transition ${ selectedAgeRange.label === range.label ? 'bg-sky-600 text-white border-sky-600 shadow-sm' : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50' }`}>
                {range.label}
              </button>
            ))}
          </div>

          <label className="block text-sm font-medium text-slate-700 mt-4 mb-2">Gênero</label>
          <div className="flex gap-2 flex-wrap">
            {(['male', 'female', 'other'] as Gender[]).map((g) => (
              <button key={g} onClick={() => toggleGender(g)} className={`px-3 py-1.5 rounded-full text-sm border transition ${ genderFilter[g] ? 'bg-sky-600 text-white border-sky-600 shadow-sm' : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50' }`} type="button">
                {g === 'male' ? 'Masculino' : g === 'female' ? 'Feminino' : 'Outro'}
              </button>
            ))}
          </div>
        </aside>

        <section className="lg:col-span-3 space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4" aria-label="Indicadores">
            {[
              { label: 'Escore Médio', value: kAvgScore, icon: <BarChart2 className="w-4 h-4 text-sky-600" /> },
              { label: '% com DES ≥ 800', value: `${kPct800}%`, icon: <ShieldCheck className="w-4 h-4 text-sky-600" /> },
              { label: 'Usuários na amostra', value: kCount, icon: <Users className="w-4 h-4 text-sky-600" /> },
              { label: 'Sinal geral', value: signal, icon: <Database className="w-4 h-4 text-sky-600" /> },
            ].map((kpi) => (
              <div key={kpi.label} className="bg-white p-4 rounded-2xl shadow-sm border flex flex-col gap-2">
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  {kpi.icon} {kpi.label}
                </div>
                <div className="text-2xl font-bold text-slate-900">{kpi.value}</div>
              </div>
            ))}
          </div>

          {/* GRÁFICOS REINTEGRADOS */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-4 rounded-2xl shadow-sm border">
              <div className="flex justify-between items-center mb-3"> {/* Container para o título e botão */}
                <h4 className="font-semibold text-slate-500">Evolução Geral do DES (12 meses)</h4>
                <button
                  onClick={() => setIsZoomed(!isZoomed)} // <-- Ação do botão
                  className="px-2 py-1 text-xs bg-sky-100 text-sky-700 rounded-md hover:bg-sky-200 transition"
                >
                  {isZoomed ? 'Ver Visão Geral' : 'Ampliar Gráfico'}
                </button>
              </div>              
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={series}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="month" />
                  <YAxis domain={isZoomed ? ['dataMin - 50', 'dataMax + 50'] : [0, 1000]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#0ea5e9" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white p-4 rounded-2xl shadow-sm border">
              <h4 className="font-semibold mb-3 text-slate-500">Distribuição de DES</h4>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={distData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="label" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#38bdf8" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white p-4 rounded-2xl shadow-sm border" id="users">
            <h4 className="font-semibold mb-3 text-slate-500">Amostra de usuários (primeiros 12)</h4>
            <div className="overflow-auto rounded-xl border">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-100 text-slate-600 text-xs">
                  <tr>
                    <th className="p-2 text-left text-black">ID</th>
                    <th className="p-2 text-left text-black">Idade</th>
                    <th className="p-2 text-left text-black">Gênero</th>
                    <th className="p-2 text-left text-black">DES Score</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.slice(0, 12).map((u) => (
                    <tr key={u.id} className="border-t">
                      <td className="p-2 text-slate-500">{u.id}</td>
                      <td className="p-2 text-slate-500">{u.age}</td>
                      <td className="p-2 text-slate-500">{u.gender}</td>
                      <td className="p-2 text-slate-500">{u.score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>

      <footer className="text-center py-6 text-sm text-slate-500 border-t border-slate-200" id="docs">
        Desenvolvido para o TCC — Métrica DES. Dados mockados; futuramente substituir por API.
      </footer>
    </div>
  )
}