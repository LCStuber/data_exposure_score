'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Search,
  Sun,
  Moon,
  Menu,
  Users,
  BarChart2,
  Database,
  ShieldCheck,
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
  Legend, 
} from 'recharts'
import useThemeColors from './hooks/use-theme-colors'

type Gender = 'male' | 'female' | 'other'
type User = { id: string; age: number; gender: Gender; score: number }

const rand = (min: number, max: number) =>
  Math.floor(Math.random() * (max - min + 1)) + min

function generateMockUsers(n = 360): User[] {
  const genders: Gender[] = ['male', 'female', 'other']
  return Array.from({ length: n }).map((_, i) => {
    const base = rand(320, 920)
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

const variableLabels: Record<string, string> = {
  NomeDeclaradoOuSugeridoPeloAutor: 'Nome declarado',
  IdadeDeclaradaOuInferidaDoAutor: 'Idade',
  GeneroAutoDeclaradoOuInferidoDoAutor: 'Gênero',
  OrientacaoSexualDeclaradaOuSugeridaPeloAutor: 'Orientação sexual',
  StatusDeRelacionamentoDeclaradoOuSugeridoPeloAutor: 'Status de relacionamento',
  ProfissaoOcupacaoDeclaradaPeloAutor: 'Profissão/Ocupação',
  NivelEducacionalDeclaradoOuInferidoDoAutor: 'Nível educacional',
  LocalizacaoPrincipalDeclaradaOuInferidaDoAutor: 'Localização principal',
  CidadesComRelevanciaPessoalParaOAutor: 'Cidades relevantes',
  CrencaReligiosaDeclaradaOuSugeridaPeloAutor: 'Crença religiosa',
  OpinioesPoliticasExpressasPeloAutor: 'Opiniões políticas',
  ExposicaoDeRelacionamentosPessoaisPeloAutor: 'Relacionamentos expostos',
  MencaoDoAutorAPosseDeCPF: 'Menção a CPF',
  MencaoDoAutorAPosseDeRG: 'Menção a RG',
  MencaoDoAutorAPosseDePassaporte: 'Menção a Passaporte',
  MencaoDoAutorAPosseDeTituloEleitor: 'Menção a Título de Eleitor',
  EtniaOuRacaAutoDeclaradaPeloAutor: 'Etnia/Raça',
  MencaoDoAutorAEnderecoResidencial: 'Endereço residencial',
  MencaoDoAutorAContatoPessoal_TelefoneEmail: 'Contato (telefone/email)',
  MencaoDoAutorADadosBancarios: 'Dados bancários',
  MencaoDoAutorACartaoDeEmbarque: 'Cartão de embarque',
  IndicadoresDeRendaPropriaMencionadosPeloAutor: 'Indicadores de renda',
  MencoesAPatrimonioPessoalDoAutor: 'Patrimônio pessoal',
  LocalDeTrabalhoOuEstudoDeclaradoPeloAutor: 'Local de trabalho/estudo',
  MencaoDoAutorARecebimentoDeBeneficioSocial: 'Benefício social',
  MencoesAoProprioHistoricoFinanceiroPeloAutor: 'Histórico financeiro',
  MencoesDoAutorAProprioHistoricoCriminal: 'Histórico criminal',
  MencaoDoAutorAPosseDeChavePix: 'Menção a Chave Pix',
}
const variableKeys = Object.keys(variableLabels)

function generateVariableSeriesData(variables: string[], totalUsers: number): Record<string, number[]> {
  const data: Record<string, number[]> = {}
  
  variables.forEach(key => {
    let baseCount = rand(10, totalUsers * 0.8)
    if (key.includes('CPF') || key.includes('RG') || key.includes('Bancarios') || key.includes('Criminal')) {
      baseCount = rand(0, totalUsers * 0.05)
    }

    data[key] = Array.from({ length: 12 }).map(() => {
      const fluctuation = rand(-Math.floor(baseCount * 0.1), Math.floor(baseCount * 0.1))
      return Math.max(0, Math.round(baseCount + fluctuation))
    })
  })
  
  return data
}

function NavBar() {
  const [open, setOpen] = useState(false)
  const [isDark, setIsDark] = useState(false)
  const searchRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains('dark'))
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        searchRef.current?.focus()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
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
    <header className="sticky top-0 z-50 border-b border-slate-200 dark:border-slate-700 bg-white/90 dark:bg-slate-900/90 backdrop-blur supports-[backdrop-filter]:bg-white/70 dark:supports-[backdrop-filter]:bg-slate-900/70">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="h-16 flex items-center justify-between">
          <div className="flex items-center gap-5">
            <Link href="#" className="pl-2 flex items-center gap-2">
              <Image
              src="/desicon.svg"
              alt="DES Logo"
              width={48}
              height={48}
              className="inline-block align-middle rounded-md"
              />
              <span className="font-semibold text-lg tracking-tight text-slate-900 dark:text-slate-100">
              DES
              </span>
            </Link>
            <nav className="hidden md:flex items-center gap-5 text-sm text-slate-600 dark:text-slate-400">
              <a href="#overview" className="hover:text-slate-900 dark:hover:text-slate-100">Visão Geral</a>
              <a href="#charts" className="hover:text-slate-900 dark:hover:text-slate-100">Gráficos</a>
              <a href="#submissions" className="hover:text-slate-900 dark:hover:text-slate-100">Submissões</a>
              <a href="#docs" className="hover:text-slate-900 dark:hover:text-slate-100">Docs</a>
            </nav>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative hidden sm:block">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 dark:text-slate-500" />
              <input
                ref={searchRef}
                placeholder="Buscar…"
                aria-label="Buscar"
                className="pl-8 pr-14 py-2 rounded-lg bg-white dark:bg-slate-800 ring-1 ring-slate-200 dark:ring-slate-700 placeholder:text-slate-400 dark:placeholder:text-slate-500 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-500 w-56 shadow-sm"
              />
              <kbd className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-slate-500 dark:text-slate-400 border border-slate-300 dark:border-slate-600 rounded px-1 bg-slate-50 dark:bg-slate-700">
                Ctrl K
              </kbd>
            </div>
            <button
              onClick={toggleTheme}
              aria-label="Alternar tema"
              className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-900 dark:text-slate-100"
              title="Alternar tema"
              type="button"
            >
              {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
            <button
              className="md:hidden p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-900 dark:text-slate-100"
              onClick={() => setOpen((v) => !v)}
              aria-label="Abrir menu"
              type="button"
            >
              <Menu className="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>
      {open && (
        <div className="md:hidden border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
          <nav className="px-4 py-3 flex flex-col gap-2 text-sm text-slate-700 dark:text-slate-300">
            <a href="#overview" className="hover:text-slate-900 dark:hover:text-slate-100" onClick={() => setOpen(false)}>Visão Geral</a>
            <a href="#charts" className="hover:text-slate-900 dark:hover:text-slate-100" onClick={() => setOpen(false)}>Gráficos</a>
            <a href="#users" className="hover:text-slate-900 dark:hover:text-slate-100" onClick={() => setOpen(false)}>Usuários</a>
          </nav>
        </div>
      )}
    </header>
  )
}


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

const lineColors = [
  '#0ea5e9', '#84cc16', '#f97316', '#ef4444', '#8b5cf6', '#ec4899',
  '#14b8a6', '#f59e0b', '#64748b', '#3b82f6', '#10b981', '#d946ef'
];

// color lookups are performed via the useThemeColors hook (see app/hooks/use-theme-colors.ts)


export default function Page() {
  const [users, setUsers] = useState<User[] | null>(null)
  const [isZoomed, setIsZoomed] = useState(false)
  const colors = useThemeColors()
  const [selectedAgeRange, setSelectedAgeRange] = useState(ageRanges[0])
  const [genderFilter, setGenderFilter] = useState({
    male: true,
    female: true,
    other: true,
  })
  const [isDark, setIsDark] = useState(false)

  // Observa mudança de classe no <html> para atualizar tema dos gráficos (sem prop drilling)
  useEffect(() => {
    const update = () => setIsDark(document.documentElement.classList.contains('dark'))
    update()
    const observer = new MutationObserver(update)
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])

  // Generate mock data only on the client to avoid SSR/client mismatch
  useEffect(() => {
    // small timeout to ensure deterministic client rendering sequence (optional)
    setUsers(generateMockUsers(360))
  }, [])
  
  const [selectedVariables, setSelectedVariables] = useState<Record<string, boolean>>(() => ({
    NomeDeclaradoOuSugeridoPeloAutor: true,
    IdadeDeclaradaOuInferidaDoAutor: true,
    MencaoDoAutorADadosBancarios: true,
  }));

  const toggleVariable = (key: string) => {
    setSelectedVariables(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

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

  const filtered = useMemo(() => {
    if (!users) return []
    return users.filter(
      (u) =>
        u.age >= selectedAgeRange.min &&
        u.age <= selectedAgeRange.max &&
        allowed.includes(u.gender)
    )
  }, [users, selectedAgeRange, allowed])
  
  const scores = useMemo(() => (filtered.length ? filtered.map((u) => u.score) : []), [filtered])
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

  const series = useMemo(() => {
    if (filtered.length === 0) {
      return Array.from({ length: 12 }).map((_, m) => ({ month: `${m + 1}`, value: 0 }));
    }
    const baselineAvg = avg(scores);
    const amplitude = baselineAvg * 0.05;
    return Array.from({ length: 12 }).map((_, m) => ({
      month: `${m + 1}`,
      value: Math.round(
        Math.max(0, Math.min(1000,
          baselineAvg +
          Math.sin((m / 11) * Math.PI * 2) * amplitude +
          rand(-20, 20)
        ))
      )
    }));
  }, [filtered, scores]);

  const variableSeriesData = useMemo(() => generateVariableSeriesData(variableKeys, users ? users.length : 0), [users]);

  const formattedVariableChartData = useMemo(() => {
    return Array.from({ length: 12 }).map((_, monthIndex) => {
      const monthData: { month: string; [key: string]: string | number } = {
        month: `${monthIndex + 1}`,
      };
      variableKeys.forEach(key => {
        monthData[key] = variableSeriesData[key][monthIndex];
      });
      return monthData;
    });
  }, [variableSeriesData]);


  if (!users) {
    return (
      <div className="bg-[var(--color-bg)] min-h-screen transition-colors duration-800">
        
        <NavBar />
        <main className="max-w-7xl mx-auto p-6">
          <div className="rounded-2xl p-6 bg-[var(--color-card)] border border-[var(--color-border)] shadow-sm">
            <h2 className="text-lg font-semibold text-[var(--color-foreground)]">Carregando dados…</h2>
            <p className="text-sm mt-2 text-[var(--color-muted)]">Gerando dados de exemplo no cliente para evitar inconsistência entre servidor e cliente.</p>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="bg-[var(--color-bg)] min-h-screen transition-colors duration-800">
      
      <NavBar />
      <section id="overview" className="border-b border-[var(--color-border)] bg-gradient-to-br from-[var(--color-card)] to-[var(--color-bg)]">
        <div className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">DES Dashboard</h1>
            {/* <p className="text-sm md:text-base text-[var(--color-muted)] mt-1">Índice de Exposição Digital — Bluesky (dados de exemplo)</p> */}
            <p className="text-sm md:text-base text-[var(--color-muted)] mt-1">Índice de Exposição Digital — Estudo de caso no Bluesky</p>
          </div>
            {/* <button className="px-3 py-2 rounded-xl text-white text-sm shadow-sm bg-[var(--color-accent)] hover:brightness-90">Exportar</button> */}
        </div>
      </section>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-4 gap-6" id="charts">
        <aside className="lg:col-span-1 bg-[var(--color-card)] border border-[var(--color-border)] rounded-2xl p-5 shadow-sm sticky top-24 h-fit">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-[var(--color-muted)]">Filtros</h3>
            <button onClick={clearFilters} className="text-sm text-[var(--color-accent)] hover:underline" type="button">
              Limpar
            </button>
          </div>
          <label className="block text-sm font-medium text-[var(--color-foreground)] mb-2">Idade</label>
          <div className="flex flex-wrap gap-2">
            {ageRanges.map((range) => (
              <button key={range.label} onClick={() => setSelectedAgeRange(range)} type="button" className={`px-3 py-1.5 rounded-full text-sm border transition ${ selectedAgeRange.label === range.label ? 'bg-[var(--color-accent)] text-white border-[var(--color-accent)] shadow-sm' : 'bg-[var(--color-card)] text-[var(--color-foreground)] border-[var(--color-border)] hover:bg-[var(--color-muted)]' }`}>
                {range.label}
              </button>
            ))}
          </div>
          <label className="block text-sm font-medium text-[var(--color-foreground)] mt-4 mb-2">Gênero</label>
          <div className="flex gap-2 flex-wrap">
            {(['male', 'female', 'other'] as Gender[]).map((g) => (
              <button key={g} onClick={() => toggleGender(g)} className={`px-3 py-1.5 rounded-full text-sm border transition ${ genderFilter[g] ? 'bg-[var(--color-accent)] text-white border-[var(--color-accent)] shadow-sm' : 'bg-[var(--color-card)] text-[var(--color-foreground)] border-[var(--color-border)] hover:bg-[var(--color-muted)]' }`} type="button">
                {g === 'male' ? 'Masculino' : g === 'female' ? 'Feminino' : 'Outro'}
              </button>
            ))}
          </div>
        </aside>

        <section className="lg:col-span-3 space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4" aria-label="Indicadores">
            {[
              { label: 'Escore Médio', value: kAvgScore, icon: <BarChart2 className="w-4 h-4 text-[var(--color-accent)]" /> },
              { label: '% com DES ≥ 800', value: `${kPct800}%`, icon: <ShieldCheck className="w-4 h-4 text-[var(--color-accent)]" /> },
              { label: 'Usuários na amostra', value: kCount, icon: <Users className="w-4 h-4 text-[var(--color-accent)]" /> },
              { label: 'Sinal geral', value: signal, icon: <Database className="w-4 h-4 text-[var(--color-accent)]" /> },
            ].map((kpi) => (
              <div key={kpi.label} className="bg-[var(--color-card)] p-4 rounded-2xl shadow-sm border border-[var(--color-border)] flex flex-col gap-2">
                <div className="flex items-center gap-2 text-sm text-[var(--color-muted)]">
                  {kpi.icon} {kpi.label}
                </div>
                <div className="text-2xl font-bold text-[var(--color-foreground)]">{kpi.value}</div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-[var(--color-card)] p-4 rounded-2xl shadow-sm border border-[var(--color-border)]">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold text-[var(--color-muted)]">Evolução Geral do DES (12 meses)</h4>
                <button
                  onClick={() => setIsZoomed(!isZoomed)}
                  className="px-2 py-1 text-xs rounded-md transition text-[var(--color-accent)] bg-[var(--color-accent-100)] hover:brightness-95"
                >
                  {isZoomed ? 'Ver Visão Geral' : 'Ampliar Gráfico'}
                </button>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={series} margin={{ top: 8, right: 8, left: 4, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                  <XAxis
                    dataKey="month"
                    tick={{ fill: colors.muted, fontSize: 12 }}
                    stroke={colors.foreground}
                  />
                  <YAxis
                    domain={isZoomed ? ['dataMin - 50', 'dataMax + 50'] : [0, 1000]}
                    tick={{ fill: colors.muted, fontSize: 12 }}
                    stroke={colors.foreground}
                  />
                  <Tooltip
                    contentStyle={{
                      background: colors.card,
                      border: `1px solid ${colors.border}`,
                      borderRadius: 8,
                      color: colors.foreground,
                      fontSize: 12,
                    }}
                    labelStyle={{ color: colors.muted }}
                  />
                  <Line type="monotone" dataKey="value" stroke={colors.accent} strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-[var(--color-card)] p-4 rounded-2xl shadow-sm border border-[var(--color-border)]">
              <h4 className="font-semibold mb-3 text-[var(--color-muted)]">Distribuição de DES</h4>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={distData} margin={{ top: 8, right: 8, left: 4, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                  <XAxis
                    dataKey="label"
                    tick={{ fill: colors.muted, fontSize: 11 }}
                    stroke={colors.foreground}
                  />
                  <YAxis
                    tick={{ fill: colors.muted, fontSize: 11 }}
                    stroke={colors.foreground}
                  />
                  <Tooltip
                    contentStyle={{
                      background: colors.card,
                      border: `1px solid ${colors.border}`,
                      borderRadius: 8,
                      color: colors.foreground,
                      fontSize: 12,
                    }}
                    labelStyle={{ color: colors.muted }}
                  />
                  <Bar dataKey="value" fill={colors.accent} radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="bg-[var(--color-card)] p-4 rounded-2xl shadow-sm border border-[var(--color-border)] lg:col-span-2">
            <h4 className="font-semibold text-[var(--color-muted)]">Evolução Temporal por Variável (aparições em 12 meses)</h4>
            
            <div className="mt-4 mb-4 border-t border-b border-[var(--color-border)] py-3">
              <h5 className="text-sm font-medium text-[var(--color-muted)] mb-2">Selecione as variáveis para exibir:</h5>
              <div className="max-h-32 overflow-y-auto pr-2 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-4 gap-y-2">
                {Object.entries(variableLabels).map(([key, label]) => (
                  <label key={key} className="flex items-center gap-2 text-sm cursor-pointer">
                    <input
                      type="checkbox"
                      checked={!!selectedVariables[key]}
                      onChange={() => toggleVariable(key)}
                      className="h-4 w-4 rounded border-[var(--color-border)] bg-[var(--color-card)] accent-[var(--color-accent)] focus:ring-[var(--color-accent)]"
                    />
                    <span className={'text-[var(--color-foreground)]'}>{label}</span>
                  </label>
                ))}
              </div>
            </div>

            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={formattedVariableChartData} margin={{ top: 10, right: 12, left: 4, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                <XAxis
                  dataKey="month"
                  label={{ value: 'Mês', position: 'insideBottom', fill: colors.muted, offset: -2 }}
                  tick={{ fill: colors.muted, fontSize: 11 }}
                  stroke={colors.foreground}
                />
                <YAxis
                  label={{ value: 'Aparições', angle: -90, position: 'insideLeft', fill: colors.muted}}
                  tick={{ fill: colors.muted, fontSize: 11 }}
                  stroke={colors.foreground}

                />
                <Tooltip
                  contentStyle={{
                    background: colors.card,
                    border: `1px solid ${colors.border}`,
                    borderRadius: 8,
                    color: colors.foreground,
                    fontSize: 12,
                  }}
                  labelStyle={{ color: colors.muted }}
                />
                <Legend
                  wrapperStyle={{ color: colors.foreground, fontSize: 12}}
                  iconSize={12}
                />
                {Object.keys(selectedVariables)
                  .filter(key => selectedVariables[key])
                  .map((key, index) => (
                    <Line
                      key={key}
                      type="monotone"
                      dataKey={key}
                      name={variableLabels[key]}
                      stroke={lineColors[index % lineColors.length]}
                      strokeWidth={2}
                      dot={false}
                    />
                  ))}
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-[var(--color-card)] p-4 rounded-2xl shadow-sm border border-[var(--color-border)]" id="users">
            <h4 className="font-semibold mb-3 text-[var(--color-muted)]">Amostra de usuários (primeiros 12)</h4>
            <div className="overflow-auto rounded-xl border border-[var(--color-border)]">
              <table className="min-w-full text-sm">
                <thead className="bg-[var(--color-card)] text-[var(--color-muted)] text-xs">
                  <tr>
                    <th className="p-2 text-left text-[var(--color-foreground)]">ID</th>
                    <th className="p-2 text-left text-[var(--color-foreground)]">Idade</th>
                    <th className="p-2 text-left text-[var(--color-foreground)]">Gênero</th>
                    <th className="p-2 text-left text-[var(--color-foreground)]">DES Score</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.slice(0, 12).map((u) => (
                    <tr key={u.id} className="border-t border-[var(--color-border)]">
                      <td className="p-2 text-[var(--color-muted)]">{u.id}</td>
                      <td className="p-2 text-[var(--color-muted)]">{u.age}</td>
                      <td className="p-2 text-[var(--color-muted)]">{u.gender}</td>
                      <td className="p-2 text-[var(--color-muted)]">{u.score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </main>

      <footer className="text-center py-6 text-sm text-[var(--color-muted)] border-t border-[var(--color-border)]" id="docs">
        Desenvolvido para o TCC — Métrica DES. Dados mockados; futuramente substituir por API.
      </footer>
    </div>
  )
}