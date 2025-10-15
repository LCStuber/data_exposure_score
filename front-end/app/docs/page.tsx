import React from 'react'
import Sidebar from './Sidebar'

export default function DocsPage() {
  return (
    <>
      <Sidebar />
      <article className="lg:col-span-3 space-y-6">
        <section id="introduction" className="rounded-2xl p-6 bg-[var(--color-card)] border border-[var(--color-border)]">
          <h1 className="text-2xl font-bold text-[var(--color-foreground)]">Introdução</h1>
          <p className="text-sm mt-2 mb-5 text-[var(--color-muted)] text-justify">Bem-vindo à documentação do DES. Aqui você pode entender o desenvolvimento do projeto, etapas alcançadas e como funciona.</p>
          <h2 className='text-2xl font-bold text-[var(--color-foreground)]'>Siginificado do projeto</h2>
          <p className="text-sm mt-2 text-[var(--color-muted)] text-justify"> Primeiro vamos explicar o que é o DES, o significado é <b className='text-[var(--color-muted)]'>Data exposure score</b>, ou em português, escore de exposição de dados.</p>
          <p className="text-sm mt-2 text-[var(--color-muted)] text-justify">O DES é uma ferramenta desenvolvida para analisar a exposição de dados em redes sociais com dados públicos. Ele ajuda a identificar vulnerabilidades e riscos associados à exposição inadvertida de informações sensíveis.</p>
          <p className="text-sm mt-2 text-[var(--color-muted)] text-justify">Por fim o projeto visa fornecer uma maneira de medir e mitigar esses riscos, permitindo que os usuários tenham um maior controle sobre suas informações pessoais.</p>
        </section>

        <section id="methodology" className="rounded-2xl p-6 bg-[var(--color-card)] border border-[var(--color-border)]">
          <h2 className="text-2xl font-semibold text-[var(--color-foreground)]">Metodologia</h2>
          <p className="text-sm mt-2 text-[var(--color-muted)] text-justify">O desenvolvimento do projeto foi estruturado em etapas sequenciais. Inicialmente, analisaram-se as restrições legais impostas pela Lei Geral de Proteção de Dados (LGPD), o que orientou a escolha das redes sociais como principal fonte de dados públicos. Em seguida, definiu-se a plataforma Bluesky como ambiente de coleta, pela disponibilidade de API aberta (AtProto) e gratuita. Essa característica elimina barreiras financeiras e restrições de acesso presentes em outras redes sociais consolidadas, como o X (antigo Twitter), permitindo uma coleta transparente e ética conforme os termos de uso da plataforma. </p>
          <p className="text-sm mt-2 text-[var(--color-muted)] text-justify">A coleta de dados foi realizada por meio da API AtProto, com múltiplos scripts desenvolvidos em Python para automatizar a extração de seguidores e postagens públicas de contas com alto volume de interação. O resultado foi um volume expressivo de postagens e metadados utilizados como base para a análise de exposição.</p>
          <p className="text-sm mt-2 text-[var(--color-muted)] text-justify">O back-end do sistema foi implementado em Python, com armazenamento em Amazon DocumentDB adequado à manipulação de grandes volumes de dados semiestruturados e não estruturados.</p>
          <p className="text-sm mt-2 text-[var(--color-muted)] text-justify">A análise automática das postagens é realizada por um modelo de linguagem open source, especificamente o meta-llama/Llama-2-13b-hf, executado diretamente.</p>
          <p className="text-sm mt-2 text-[var(--color-muted)] text-justify">Ao final do processo, o sistema calcula o escore DES, baseado em critérios de impacto e explorabilidade das informações identificadas nas postagens públicas. O resultado é disponibilizado de forma assíncrona via API, permitindo visualização e atualização conforme o instante da solicitação da análise.</p>
        </section>

        {/* <section id="installation" className="rounded-2xl p-6 bg-[var(--color-card)] border border-[var(--color-border)]">
          <h2 className="text-xl font-semibold text-[var(--color-foreground)]">Instalação</h2>
          <p className="text-sm mt-2 text-[var(--color-muted)]">Instale as dependências e inicie o front-end:</p>
          <pre className="mt-3 p-3 bg-slate-50 dark:bg-slate-800 rounded text-sm overflow-auto border border-[var(--color-border)]"><code>npm install{`\n`}npm run dev</code></pre>
        </section>

        <section id="usage" className="rounded-2xl p-6 bg-[var(--color-card)] border border-[var(--color-border)]">
          <h2 className="text-xl font-semibold text-[var(--color-foreground)]">Uso Rápido</h2>
          <p className="text-sm mt-2 text-[var(--color-muted)]">Exemplo de componente:</p>
          <div className="mt-3">
            <button className="px-4 py-2 rounded-xl bg-[var(--color-accent)] text-white">Botão de Exemplo</button>
          </div>
        </section>

        <section id="components" className="rounded-2xl p-6 bg-[var(--color-card)] border border-[var(--color-border)]">
          <h2 className="text-xl font-semibold text-[var(--color-foreground)]">Componentes</h2>
          <p className="text-sm mt-2 text-[var(--color-muted)]">Documente seus componentes aqui: botões, formulários, cards e mais.</p>
        </section>

        <section id="theming" className="rounded-2xl p-6 bg-[var(--color-card)] border border-[var(--color-border)]">
          <h2 className="text-xl font-semibold text-[var(--color-foreground)]">Theming</h2>
          <p className="text-sm mt-2 text-[var(--color-muted)]">O projeto usa CSS custom properties e classes utilitárias Tailwind para cores e espaçamento. Veja <code>app/globals.css</code> para as variáveis.</p>
        </section> */}
      </article>
    </>
  )
}
