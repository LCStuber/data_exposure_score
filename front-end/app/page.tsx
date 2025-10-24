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

function NavBar() {
  const [open, setOpen] = useState(false)
  const [isDark, setIsDark] = useState(false)
  const searchRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const storedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (storedTheme === 'dark' || (!storedTheme && prefersDark)) {
      document.documentElement.classList.add('dark');
      setIsDark(true);
    } else {
      document.documentElement.classList.remove('dark');
      setIsDark(false);
    }

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
              <a href="docs" className="hover:text-slate-900 dark:hover:text-slate-100">Docs</a> 
            </nav>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative hidden sm:block">
              <Link
                href="docs"
                className="hidden sm:inline-flex items-center px-3 py-1.5 rounded-lg text-sm text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition"
                title="Ir para documentação"
              >
                Documentação
              </Link>
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
            <a href="#docs" className="hover:text-slate-900 dark:hover:text-slate-100" onClick={() => setOpen(false)}>Docs</a> 
          </nav>
        </div>
      )}
    </header>
  )
}

const ageLabels = ["Todos", "< 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+", "Outros"];
const genderLabels = ["Todos", "Masculino", "Feminino", "Outros"];

const lineColors = [
  '#0ea5e9', '#84cc16', '#f97316', '#ef4444', '#8b5cf6', '#ec4899',
  '#14b8a6', '#f59e0b', '#64748b', '#3b82f6', '#10b981', '#d946ef'
];

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

  const [selectedAgeRange, setSelectedAgeRange] = useState(ageLabels[0]);
  const [selectedGender, setSelectedGender] = useState(genderLabels[0]);

  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    const update = () => setIsDark(document.documentElement.classList.contains('dark'))
    update()
    const observer = new MutationObserver(update)
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])

  useEffect(() => {

      fetch('https://api.des.lcstuber.net/aggregates')
        .then((r) => r.json())
        .then((data) => {
          const item = Array.isArray(data) ? data[0] : data
          setAggregates(item.aggregates ?? item)
        })
        .catch((err) => {
          console.error('Failed to load aggregates:', err)
        })
    }, [])
    // Use the local file path for testing if needed, otherwise use the API endpoint
    // fetch('/aggregates.json') // For local testing
    
  const [selectedVariables, setSelectedVariables] = useState<Record<string, boolean>>(() => ({
    NomeDeclaradoOuSugeridoPeloAutor: true,
    IdadeDeclaradaOuInferidaDoAutor: true,
    MencaoDoAutorADadosBancarios: true,
    OpinioesPoliticasExpressasPeloAutor: true,
    ExposicaoDeRelacionamentosPessoaisPeloAutor: true,
    IndicadoresDeRendaPropriaMencionadosPeloAutor: true,
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

  const isAgeFiltered = selectedAgeRange !== 'Todos';
  const isGenderFiltered = selectedGender !== 'Todos';
    const { barData, barTitle } = useMemo(() => {
  if (!aggregates) return { barData: [], barTitle: 'Top 5 variáveis mais frequentes' };

  let counts: Record<string, number> = {};
  let title = 'Top 5 variáveis mais frequentes'; 

  try {
    if (isAgeFiltered && isGenderFiltered) {
      counts = aggregates.by_age_and_gender_field_counts?.[selectedAgeRange]?.[selectedGender] ?? {};
      title += ` (${selectedAgeRange} & ${selectedGender})`;
    } else if (isAgeFiltered) {
      counts = aggregates.by_age_field_counts?.[selectedAgeRange] ?? {}; 
      title += ` (${selectedAgeRange})`;
    } else if (isGenderFiltered) {
      counts = aggregates.by_gender_field_counts?.[selectedGender] ?? {}; 
      title += ` (${selectedGender})`;
    } else {
      counts = aggregates.field_counts_overall ?? {};
    }
  } catch (e) {
    console.error('Erro ao acessar contagens filtradas:', e);
  }

  if (typeof counts !== 'object' || counts === null) {
    console.warn('Counts data is not an object:', counts);
    counts = {};
  }


  const arr = Object.entries(counts)
    .map(([key, val]) => ({
      key,
      label: variableLabels[key] ?? key,
      value: Number(val ?? 0),
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 5);

  return { barData: arr, barTitle: title };

}, [aggregates, isAgeFiltered, isGenderFiltered, selectedAgeRange, selectedGender]);

  const kpiData = useMemo(() => {
    if (!aggregates) return defaultKpiData;

    try {
      if (isAgeFiltered && isGenderFiltered) {
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
      return defaultKpiData; 
    }

    return aggregates.overall ?? defaultKpiData;
  }, [aggregates, selectedAgeRange, selectedGender, isAgeFiltered, isGenderFiltered]);

  const kAvgScore = Math.round(kpiData?.avg_des ?? 0)
  const kCount = kpiData?.count ?? 0
  const kPct800 = (kpiData?.percent_gt_800 ?? 0).toFixed(1)
  const signal = kAvgScore >= 800 ? 'Alto' : kAvgScore >= 600 ? 'Médio' : 'Baixo'

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
          avg_des = monthData?.avg_des ?? 0;
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


  const { monthlyVariableData, monthlyVariableTitle, monthlyVariableNote } = useMemo(() => {
    if (!aggregates) return { monthlyVariableData: [], monthlyVariableTitle: 'Visão Geral das Variáveis das Variáveis', monthlyVariableNote: '' };

    let monthlySource: any = null;
    let title = 'Visão Geral das Variáveis';
    let note = 'Comportamento geral.';

    try {
        if (isAgeFiltered && isGenderFiltered) {
            monthlySource = aggregates?.monthly_by_age_and_gender_field_counts;
            title = `Visão Geral das Variáveis (${selectedAgeRange} & ${selectedGender})`;
            note = `Comportamento com filtros (${selectedAgeRange}) e Gênero (${selectedGender}).`;
        } else if (isAgeFiltered) {
            monthlySource = aggregates?.monthly_by_age_field_counts;
            title = `Visão Geral das Variáveis (${selectedAgeRange})`;
            note = `Comportamento com filtro (${selectedAgeRange}).`;
        } else if (isGenderFiltered) {
            monthlySource = aggregates?.monthly_by_gender_field_counts;
            title = `Visão Geral das Variáveis (${selectedGender})`;
            note = `Comportamento com filtro (${selectedGender}).`;
        } else {
            monthlySource = aggregates?.monthly_field_counts;
        }
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
        const monthEntry: { month: string;[key: string]: number | string } = { month };
        let monthDataForFilters = monthlySource[month];

            if (isAgeFiltered && isGenderFiltered) {
                 monthDataForFilters = monthDataForFilters?.[selectedAgeRange]?.[selectedGender] ?? {};
            } else if (isAgeFiltered) {
                 monthDataForFilters = monthDataForFilters?.[selectedAgeRange] ?? {};
            } else if (isGenderFiltered) {
                 monthDataForFilters = monthDataForFilters?.[selectedGender] ?? {};
            }
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


            activeVariableKeys.forEach(key => {
                monthEntry[key] = monthDataForFilters[key] ?? 0; 
            });
        // Populate counts for active variables
        activeVariableKeys.forEach(key => {
          monthEntry[key] = monthDataForFilters[key] ?? 0; // Use count or 0 if missing
        });

        return monthEntry;
      });

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


  if (!aggregates) {
    return (
      <div className="bg-slate-50 dark:bg-slate-950 min-h-screen transition-colors duration-300"> 
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
                className={`px-3 py-1.5 rounded-full text-xs sm:text-sm border transition ${
                selectedAgeRange === label
                    ? 'bg-sky-600 text-white border-sky-600 shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700'
                }`}
            >
                {label === "Outros" ? "Não Identificado" : label}
            </button>
            ))}

          </div>
          <label className="block text-sm font-medium mt-4 mb-2">Gênero</label>
          <div className="flex gap-2 flex-wrap">
            {genderLabels.map((label) => (
            <button
                key={label}
                onClick={() => handleSelectGender(label)}
                className={`px-3 py-1.5 rounded-full text-xs sm:text-sm border transition ${
                selectedGender === label
                    ? 'bg-sky-600 text-white border-sky-600 shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700'
                }`}
                type="button"
            >
                {label === "Outros" ? "Não Identificado" : label}
            </button>
            ))}

          </div>
        </aside>


        <section className="lg:col-span-3 space-y-6">

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

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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


          <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800">
            <h4 className="font-semibold text-slate-600 dark:text-slate-400 text-sm sm:text-base">{monthlyVariableTitle}</h4>
            <p className="text-xs text-slate-500 dark:text-slate-500 -mt-1 mb-2">{monthlyVariableNote}</p>


            

            <div>
            <ResponsiveContainer width="100%" height={350}>
            <BarChart
        data={barData}
        layout="vertical"
        margin={{ top: 10, right: 30, left: 80, bottom: 10 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
        <XAxis type="number" stroke={colors.foreground} />
        <YAxis
          dataKey="label"
          type="category"
          stroke={colors.foreground}
          width={180}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: colors.card,
            borderColor: colors.border,
            color: colors.foreground,
          }}
        />
        <Bar dataKey="value" fill={colors.accent} radius={[4, 4, 4, 4]} />
      </BarChart>
            </ResponsiveContainer>
            </div>
            </div>

        </section>
      </main>

      <footer className="text-center py-6 text-sm text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-slate-800" id="docs">
        Desenvolvido para o TCC — Métrica DES. Dados provenientes do endpoint de agregados (produção).
      </footer>
    </div>
  )
}