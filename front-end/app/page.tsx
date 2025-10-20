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
// Assuming useThemeColors exists and works as intended
// If not, replace calls like colors.accent with static values e.g., "'#0ea5e9'"
// For simplicity, I'll assume it exists and returns an object like { border: '#e2e8f0', card: '#ffffff', foreground: '#0f172a', muted: '#64748b', accent: '#0ea5e9', accent100: '#e0f2fe' } for light mode
// And corresponding dark mode values. You might need to adjust this hook or replace its usage.
import useThemeColors from './hooks/use-theme-colors'


// Definição dos labels das variáveis (unchanged)
const variableLabels: Record<string, string> = {
  NomeDeclaradoOuSugeridoPeloAutor: 'Nome declarado',
  IdadeDeclaradaOuInferidaDoAutor: 'Idade',
  GeneroAutoDeclaradoOuInferidoDoAutor: 'Gênero',
  OrientacaoSexualDeclaradaOuSugeridaPeloAutor: 'Orientação sexual',
  StatusDeRelacionamentoDeclaradoOuSugeridoDoAutor: 'Status de relacionamento',
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

// Componente NavBar (sem alterações)
function NavBar() {
  const [open, setOpen] = useState(false)
  const [isDark, setIsDark] = useState(false)
  const searchRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Initialize theme based on localStorage or system preference
    const storedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (storedTheme === 'dark' || (!storedTheme && prefersDark)) {
      document.documentElement.classList.add('dark');
      setIsDark(true);
    } else {
      document.documentElement.classList.remove('dark');
      setIsDark(false);
    }

    // Keyboard shortcut listener
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
              src="/desicon.svg" // Assuming desicon.svg is in the public folder
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
              <a href="#docs" className="hover:text-slate-900 dark:hover:text-slate-100">Docs</a> {/* Changed link to match footer id */}
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
            <a href="#docs" className="hover:text-slate-900 dark:hover:text-slate-100" onClick={() => setOpen(false)}>Docs</a> {/* Changed link */}
          </nav>
        </div>
      )}
    </header>
  )
}

// Configurações (unchanged)
const ageLabels = ["Todos", "< 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+", "Outros"];
const genderLabels = ["Todos", "Masculino", "Feminino", "Outros"];

const lineColors = [
  '#0ea5e9', '#84cc16', '#f97316', '#ef4444', '#8b5cf6', '#ec4899',
  '#14b8a6', '#f59e0b', '#64748b', '#3b82f6', '#10b981', '#d946ef'
];

// Default empty KPI structure for fallbacks
const defaultKpiData = {
    count: 0,
    avg_des: 0,
    percent_gt_800: 0,
    des_range_counts: {},
};

export default function Page() {
  const [aggregates, setAggregates] = useState<any | null>(null)
  const [isZoomed, setIsZoomed] = useState(false)
  const colors = useThemeColors()

  // Estado dos filtros
  const [selectedAgeRange, setSelectedAgeRange] = useState(ageLabels[0]);
  const [selectedGender, setSelectedGender] = useState(genderLabels[0]);

  const [isDark, setIsDark] = useState(false)

  // Hook para tema (unchanged)
  useEffect(() => {
    const update = () => setIsDark(document.documentElement.classList.contains('dark'))
    update()
    const observer = new MutationObserver(update)
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])

  // Fetch dos dados (unchanged)
  useEffect(() => {
      // Use the local file path for testing if needed, otherwise use the API endpoint
      // fetch('/aggregates.json') // For local testing
      fetch('https://api.des.lcstuber.net/aggregates') // For production endpoint
        .then((r) => r.json())
        .then((data) => {
          // The API might return an array with one item, or just the item
          const item = Array.isArray(data) ? data[0] : data
          // Check if the actual aggregates are nested under an 'aggregates' key
          setAggregates(item.aggregates ?? item)
        })
        .catch((err) => {
          console.error('Failed to load aggregates:', err)
          // Optionally set aggregates to an empty object or handle the error state
          // setAggregates({});
        })
    }, [])

  // Estado do seletor de variáveis (unchanged)
  const [selectedVariables, setSelectedVariables] = useState<Record<string, boolean>>(() => ({
    NomeDeclaradoOuSugeridoPeloAutor: true,
    IdadeDeclaradaOuInferidaDoAutor: true,
    MencaoDoAutorADadosBancarios: true,
    OpinioesPoliticasExpressasPeloAutor: true,
    ExposicaoDeRelacionamentosPessoaisPeloAutor: true,
    IndicadoresDeRendaPropriaMencionadosPeloAutor: true,
    // Initialize others as false or based on default view preferences
    ...Object.fromEntries(variableKeys.filter(k => ![
        'NomeDeclaradoOuSugeridoPeloAutor',
        'IdadeDeclaradaOuInferidaDoAutor',
        'MencaoDoAutorADadosBancarios',
        'OpinioesPoliticasExpressasPeloAutor',
        'ExposicaoDeRelacionamentosPessoaisPeloAutor',
        'IndicadoresDeRendaPropriaMencionadosPeloAutor'
    ].includes(k)).map(k => [k, false]))
  }));

  const toggleVariable = (key: string) => {
    setSelectedVariables(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  // Handlers dos filtros (unchanged)
  const handleSelectAge = (age: string) => {
    setSelectedAgeRange(age);
  };

  const handleSelectGender = (gender: string) => {
    setSelectedGender(gender);
  };

  const clearFilters = () => {
    setSelectedAgeRange('Todos');
    setSelectedGender('Todos');
  };

  // Filter status checks (unchanged)
  const isAgeFiltered = selectedAgeRange !== 'Todos';
  const isGenderFiltered = selectedGender !== 'Todos';

  // 1. Dados para os KPIs (logic unchanged)
  const kpiData = useMemo(() => {
    if (!aggregates) return defaultKpiData; // Use default on initial load

    try {
      if (isAgeFiltered && isGenderFiltered) {
        // Access combined data, provide default if specific combo is missing
        return aggregates?.by_age_and_gender?.[selectedAgeRange]?.[selectedGender] ?? defaultKpiData;
      }
      if (isAgeFiltered) {
        return aggregates?.by_age?.[selectedAgeRange] ?? defaultKpiData;
      }
      if (isGenderFiltered) {
        return aggregates?.by_gender?.[selectedGender] ?? defaultKpiData;
      }
    } catch (e) {
      console.error(`Error accessing KPI data for filters: ${selectedAgeRange} / ${selectedGender}`, e);
      return defaultKpiData; // Return default on error
    }

    return aggregates.overall ?? defaultKpiData;
  }, [aggregates, selectedAgeRange, selectedGender, isAgeFiltered, isGenderFiltered]);

  // Valores dos KPIs (logic unchanged)
  const kAvgScore = Math.round(kpiData?.avg_des ?? 0)
  const kCount = kpiData?.count ?? 0
  const kPct800 = (kpiData?.percent_gt_800 ?? 0).toFixed(1)
  const signal = kAvgScore >= 800 ? 'Alto' : kAvgScore >= 600 ? 'Médio' : 'Baixo'

  // 2. Dados para o Gráfico de Distribuição (Barras) (logic unchanged)
  const { distData, distTitle } = useMemo(() => {
    const ranges = kpiData?.des_range_counts;

    if (ranges && Object.keys(ranges).length > 0) {
      const data = Object.entries(ranges).map(([label, value]) => ({ label, value: value as number }));

      let title = 'Distribuição de DES (Geral)';
      if (isAgeFiltered && isGenderFiltered) {
        title = `Distribuição DES (${selectedAgeRange} & ${selectedGender})`;
      } else if (isAgeFiltered) {
        title = `Distribuição DES (${selectedAgeRange})`;
      } else if (isGenderFiltered) {
        title = `Distribuição DES (${selectedGender})`;
      }

      return { distData: data, distTitle: title };
    }

     return { distData: [], distTitle: 'Distribuição de DES' };
  }, [kpiData, isAgeFiltered, isGenderFiltered, selectedAgeRange, selectedGender]);


  // 3. Dados para o Gráfico de Evolução DES (Linha) (logic unchanged)
  const { series, seriesNote } = useMemo(() => {
    if (!aggregates) return { series: [], seriesNote: 'Carregando...' };

    let dataToProcess: any = null;
    let note = "Exibindo dados gerais.";

    try {
        if (isAgeFiltered && isGenderFiltered) {
            dataToProcess = aggregates.monthly_by_age_and_gender;
            note = `Exibindo dados por Idade (${selectedAgeRange}) e Gênero (${selectedGender}).`;
        } else if (isAgeFiltered) {
            dataToProcess = aggregates.monthly_by_age;
            note = `Exibindo dados por Idade (${selectedAgeRange}).`;
        } else if (isGenderFiltered) {
            dataToProcess = aggregates.monthly_by_gender;
            note = `Exibindo dados por Gênero (${selectedGender}).`;
        } else {
            dataToProcess = aggregates.monthly_general;
        }

        if (!dataToProcess) {
             console.warn("Source data for series is null/undefined");
             return { series: [], seriesNote: 'Dados não disponíveis para a seleção.' };
        }

        const months = Object.keys(dataToProcess).sort();
        const processedSeries = months.map(m => {
            let monthData = dataToProcess[m];
            let avg_des = 0;

            if (isAgeFiltered && isGenderFiltered) {
                avg_des = monthData?.[selectedAgeRange]?.[selectedGender]?.avg_des ?? 0;
            } else if (isAgeFiltered) {
                avg_des = monthData?.[selectedAgeRange]?.avg_des ?? 0;
            } else if (isGenderFiltered) {
                avg_des = monthData?.[selectedGender]?.avg_des ?? 0;
            } else {
                avg_des = monthData?.avg_des ?? 0; // Overall case
            }

            return {
                month: m,
                value: Math.round(avg_des)
            };
        }).filter(d => d.value > 0);

        if (processedSeries.length === 0 && (isAgeFiltered || isGenderFiltered)) {
             note = `Dados não disponíveis para a combinação ${selectedAgeRange} / ${selectedGender}.`;
        }

        return { series: processedSeries, seriesNote: note };

    } catch (e) {
        console.error("Error processing time series data:", e);
        return { series: [], seriesNote: 'Erro ao processar dados.' };
    }
  }, [aggregates, selectedAgeRange, selectedGender, isAgeFiltered, isGenderFiltered]);

  // *** FIX: Moved this hook outside the other useMemo ***
  // 5. Data for the Monthly Variable Count Evolution Line Chart
  const { monthlyVariableData, monthlyVariableTitle, monthlyVariableNote } = useMemo(() => {
    if (!aggregates) return { monthlyVariableData: [], monthlyVariableTitle: 'Evolução Mensal das Variáveis', monthlyVariableNote: '' };

    let monthlySource: any = null;
    let title = 'Evolução Mensal das Variáveis (Geral)';
    let note = 'Contagem mensal das variáveis selecionadas na amostra geral.';

    try {
        // Determine the correct data source based on filters
        if (isAgeFiltered && isGenderFiltered) {
            monthlySource = aggregates?.monthly_by_age_and_gender_field_counts;
            title = `Evolução Mensal (${selectedAgeRange} & ${selectedGender})`;
            note = `Contagem mensal para Idade (${selectedAgeRange}) e Gênero (${selectedGender}).`;
        } else if (isAgeFiltered) {
            monthlySource = aggregates?.monthly_by_age_field_counts;
            title = `Evolução Mensal (${selectedAgeRange})`;
            note = `Contagem mensal para Idade (${selectedAgeRange}).`;
        } else if (isGenderFiltered) {
            monthlySource = aggregates?.monthly_by_gender_field_counts;
            title = `Evolução Mensal (${selectedGender})`;
            note = `Contagem mensal para Gênero (${selectedGender}).`;
        } else {
            monthlySource = aggregates?.monthly_field_counts;
        }

        if (!monthlySource) {
             return { monthlyVariableData: [], monthlyVariableTitle: title, monthlyVariableNote: 'Dados não disponíveis para a seleção.' };
        }

        const months = Object.keys(monthlySource).sort();
        const activeVariableKeys = Object.entries(selectedVariables)
                                    .filter(([key, isActive]) => isActive)
                                    .map(([key]) => key);

        if (activeVariableKeys.length === 0) {
            return { monthlyVariableData: [], monthlyVariableTitle: title, monthlyVariableNote: 'Selecione pelo menos uma variável para exibir.' };
        }


        const chartData = months.map(month => {
            const monthEntry: { month: string; [key: string]: number | string } = { month };
            let monthDataForFilters = monthlySource[month];

             // Drill down if filters are applied
            if (isAgeFiltered && isGenderFiltered) {
                 monthDataForFilters = monthDataForFilters?.[selectedAgeRange]?.[selectedGender] ?? {};
            } else if (isAgeFiltered) {
                 monthDataForFilters = monthDataForFilters?.[selectedAgeRange] ?? {};
            } else if (isGenderFiltered) {
                 monthDataForFilters = monthDataForFilters?.[selectedGender] ?? {};
            }

             // Ensure monthDataForFilters is an object before proceeding
             monthDataForFilters = monthDataForFilters ?? {};


            // Populate counts for active variables
            activeVariableKeys.forEach(key => {
                monthEntry[key] = monthDataForFilters[key] ?? 0; // Use count or 0 if missing
            });

            return monthEntry;
        });

         // Add note if specific combo resulted in no data points for any selected variable
        const hasDataPoints = chartData.some(entry => activeVariableKeys.some(key => (entry[key] as number) > 0));
        if (!hasDataPoints && (isAgeFiltered || isGenderFiltered)) {
            note = `Dados de contagem mensal não disponíveis para a seleção ${selectedAgeRange} / ${selectedGender}.`;
        }


        return { monthlyVariableData: chartData, monthlyVariableTitle: title, monthlyVariableNote: note };

    } catch (e) {
        console.error("Error processing monthly variable count data:", e);
         return { monthlyVariableData: [], monthlyVariableTitle: title, monthlyVariableNote: 'Erro ao processar dados.' };
    }

  }, [aggregates, selectedAgeRange, selectedGender, isAgeFiltered, isGenderFiltered, selectedVariables]);


  // Tela de carregamento (unchanged)
  if (!aggregates) {
    return (
      <div className="bg-slate-50 dark:bg-slate-950 min-h-screen transition-colors duration-300"> {/* Use direct colors for loading */}
        <NavBar />
        <main className="max-w-7xl mx-auto p-6">
          <div className="rounded-2xl p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Carregando dados…</h2>
            <p className="text-sm mt-2 text-slate-600 dark:text-slate-400">Buscando agregados do endpoint de produção.</p>
          </div>
        </main>
      </div>
    )
  }

  // Renderização da página
  return (
    <div className="bg-slate-50 dark:bg-slate-950 min-h-screen transition-colors duration-300 text-slate-900 dark:text-slate-100">

      <NavBar />
      <section id="overview" className="border-b border-slate-200 dark:border-slate-800 bg-gradient-to-br from-white dark:from-slate-900 to-slate-50 dark:to-slate-950">
        <div className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">DES Dashboard</h1>
            <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 mt-1">Índice de Exposição Digital — Estudo de caso</p>
          </div>
        </div>
      </section>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-4 gap-6" id="charts">
        {/* Sidebar with Filters */}
        <aside className="lg:col-span-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm sticky top-24 h-fit">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-300">Filtros</h3>
            {(isAgeFiltered || isGenderFiltered) && (
                 <button onClick={clearFilters} className="text-sm text-sky-600 dark:text-sky-400 hover:underline" type="button">
                    Limpar
                 </button>
            )}
          </div>
          <label className="block text-sm font-medium mb-2">Idade</label>
          <div className="flex flex-wrap gap-2">
            {ageLabels.map((label) => (
              <button
                key={label}
                onClick={() => handleSelectAge(label)}
                type="button"
                className={`px-3 py-1.5 rounded-full text-xs sm:text-sm border transition ${ selectedAgeRange === label ? 'bg-sky-600 text-white border-sky-600 shadow-sm' : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700' }`}>
                {label}
              </button>
            ))}
          </div>
          <label className="block text-sm font-medium mt-4 mb-2">Gênero</label>
          <div className="flex gap-2 flex-wrap">
            {genderLabels.map((label) => (
              <button
                key={label}
                onClick={() => handleSelectGender(label)}
                className={`px-3 py-1.5 rounded-full text-xs sm:text-sm border transition ${ selectedGender === label ? 'bg-sky-600 text-white border-sky-600 shadow-sm' : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700' }`}
                type="button">
                {label === 'Todos' ? 'Todos' : label} {/* Display 'Todos' consistently */}
              </button>
            ))}
          </div>
        </aside>

        {/* Main Content Area */}
        <section className="lg:col-span-3 space-y-6">
          {/* KPIs */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4" aria-label="Indicadores">
            {[
              { label: 'Escore Médio', value: kAvgScore, icon: <BarChart2 className="w-4 h-4 text-sky-500" /> },
              { label: '% ≥ 800', value: `${kPct800}%`, icon: <ShieldCheck className="w-4 h-4 text-sky-500" /> },
              { label: 'Usuários', value: kCount.toLocaleString('pt-BR'), icon: <Users className="w-4 h-4 text-sky-500" /> }, // Format number
              { label: 'Sinal', value: signal, icon: <Database className="w-4 h-4 text-sky-500" /> },
            ].map((kpi) => (
              <div key={kpi.label} className="bg-white dark:bg-slate-900 p-4 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col gap-1 sm:gap-2">
                <div className="flex items-center gap-2 text-xs sm:text-sm text-slate-500 dark:text-slate-400">
                  {kpi.icon} {kpi.label}
                </div>
                <div className="text-xl sm:text-2xl font-bold">{kpi.value}</div>
              </div>
            ))}
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
             {/* Line Chart (DES Evolution) */}
             <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800">
              <div className="flex justify-between items-center mb-1">
                <h4 className="font-semibold text-slate-600 dark:text-slate-400 text-sm sm:text-base">Evolução Média DES (12m)</h4>
                <button
                  onClick={() => setIsZoomed(!isZoomed)}
                  className="px-2 py-1 text-xs rounded-md transition text-sky-600 dark:text-sky-400 bg-sky-100 dark:bg-sky-900/50 hover:brightness-95"
                  aria-label={isZoomed ? "Reduzir zoom do gráfico" : "Ampliar gráfico"}
                >
                  {isZoomed ? 'Zoom -' : 'Zoom +'}
                </button>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-500 -mt-1 mb-2">
                 {seriesNote}
              </p>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={series} margin={{ top: 8, right: 8, left: -10, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                  <XAxis
                    dataKey="month"
                    tick={{ fill: colors.muted, fontSize: 11 }}
                    stroke={colors.foreground}
                    axisLine={{ stroke: colors.border }}
                    tickLine={{ stroke: colors.border }}
                  />
                  <YAxis
                    domain={isZoomed ? ['dataMin - 50', 'dataMax + 50'] : [0, 1000]}
                    tick={{ fill: colors.muted, fontSize: 11 }}
                    stroke={colors.foreground}
                    axisLine={{ stroke: colors.border }}
                    tickLine={{ stroke: colors.border }}
                  />
                  <Tooltip
                    contentStyle={{
                      background: colors.card,
                      border: `1px solid ${colors.border}`,
                      borderRadius: 8,
                      color: colors.foreground,
                      fontSize: 12,
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)'
                    }}
                    labelStyle={{ color: colors.muted }}
                    itemStyle={{ color: colors.accent }}
                    formatter={(value: number) => [value, 'DES Médio']}
                  />
                  <Line type="monotone" dataKey="value" stroke={colors.accent} strokeWidth={2} dot={false} name="DES Médio" />
                </LineChart>
              </ResponsiveContainer>
            </div>
             {/* Bar Chart (DES Distribution) */}
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800">
              <h4 className="font-semibold mb-3 text-slate-600 dark:text-slate-400 text-sm sm:text-base">{distTitle}</h4>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={distData} margin={{ top: 8, right: 8, left: -10, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                  <XAxis
                    dataKey="label"
                    tick={{ fill: colors.muted, fontSize: 11 }}
                    stroke={colors.foreground}
                    axisLine={{ stroke: colors.border }}
                    tickLine={{ stroke: colors.border }}
                    interval={0}
                  />
                  <YAxis
                    tick={{ fill: colors.muted, fontSize: 11 }}
                    stroke={colors.foreground}
                    axisLine={{ stroke: colors.border }}
                    tickLine={{ stroke: colors.border }}
                  />
                  <Tooltip
                    contentStyle={{
                      background: colors.card,
                      border: `1px solid ${colors.border}`,
                      borderRadius: 8,
                      color: colors.foreground,
                      fontSize: 12,
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)'
                    }}
                    labelStyle={{ color: colors.muted }}
                    itemStyle={{ color: colors.accent }}
                     formatter={(value: number) => [value.toLocaleString('pt-BR'), 'Contagem']}
                  />
                  <Bar dataKey="value" fill={colors.accent} radius={[4, 4, 0, 0]} name="Contagem" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* *** FIX: Using monthlyVariable... variables here *** */}
          {/* Monthly Variable Counts Line Chart */}
          <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800">
            {/* Title and Note */}
            <h4 className="font-semibold text-slate-600 dark:text-slate-400 text-sm sm:text-base">{monthlyVariableTitle}</h4>
            <p className="text-xs text-slate-500 dark:text-slate-500 -mt-1 mb-2">{monthlyVariableNote}</p>

            {/* Variable Selector (Remains the same) */}
            <div className="mt-4 mb-4 border-t border-b border-slate-200 dark:border-slate-700 py-3">
              <h5 className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">Selecione variáveis para exibir:</h5>
              <div className="max-h-32 overflow-y-auto pr-2 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-x-4 gap-y-1.5">
                {variableKeys.map((key) => (
                  <label key={key} className="flex items-center gap-1.5 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={!!selectedVariables[key]}
                      onChange={() => toggleVariable(key)}
                      className="h-3.5 w-3.5 rounded border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sky-600 focus:ring-sky-500 focus:ring-offset-white dark:focus:ring-offset-slate-900"
                    />
                    <span className={'text-xs text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-slate-100 transition-colors'}>{variableLabels[key]}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Line Chart Container */}
            <div>
              {monthlyVariableData.length > 0 && Object.keys(selectedVariables).some(k => selectedVariables[k]) ? (
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart
                    data={monthlyVariableData} // *** FIX: Use correct data ***
                    margin={{ top: 10, right: 20, left: -10, bottom: 20 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                    <XAxis
                      dataKey="month"
                      tick={{ fill: colors.muted, fontSize: 10 }}
                      stroke={colors.foreground}
                      axisLine={{ stroke: colors.border }}
                      tickLine={{ stroke: colors.border }}
                    />
                    <YAxis
                       tick={{ fill: colors.muted, fontSize: 10 }}
                       stroke={colors.foreground}
                       axisLine={{ stroke: colors.border }}
                       tickLine={{ stroke: colors.border }}
                       tickFormatter={(value) => value.toLocaleString('pt-BR')}
                    />
                    <Tooltip
                       cursor={{ stroke: colors.border, strokeDasharray: '3 3' }}
                       contentStyle={{
                         background: colors.card,
                         border: `1px solid ${colors.border}`,
                         borderRadius: 8,
                         color: colors.foreground,
                         fontSize: 12,
                         boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)'
                       }}
                       labelStyle={{ color: colors.muted, fontWeight: 'bold' }}
                       formatter={(value: number, name: string) => [value.toLocaleString('pt-BR'), variableLabels[name] ?? name]}
                    />
                    <Legend iconType="plainline" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}/>
                    {Object.entries(selectedVariables)
                      .filter(([key, isActive]) => isActive)
                      .map(([key], index) => (
                        <Line
                          key={key}
                          type="monotone"
                          dataKey={key}
                          name={key}
                          stroke={lineColors[index % lineColors.length]}
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 4 }}
                        />
                      ))}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-10 text-slate-500 dark:text-slate-400 text-sm h-[350px] flex items-center justify-center">
                   {Object.keys(selectedVariables).some(k => selectedVariables[k])
                     ? 'Dados não disponíveis para a seleção atual.'
                     : 'Selecione uma ou mais variáveis acima para visualizar a evolução.'}
                </div>
              )}
            </div>
          </div>

        </section>
      </main>

      {/* Footer */}
      <footer className="text-center py-6 text-sm text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-slate-800" id="docs">
        Desenvolvido para o TCC — Métrica DES. Dados provenientes do endpoint de agregados (produção).
      </footer>
    </div>
  )
}