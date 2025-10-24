export default function IntroOverview() {
  return (
    <div className="space-y-6">
      {/* header com quadrado colorido */}
      <header className="flex items-center gap-4">
        {/* <div className="flex-none w-20 h-20 rounded-md bg-[var(--color-accent)] text-white flex items-center justify-center font-bold text-lg shadow">
          DES
        </div> */}

        <div className="flex-1 flex items-center justify-center">
          <p className="mt-1 text-sm text-[var(--color-muted)] max-w-xl leading-relaxed text-center">
            O Data Exposure Score (DES) mensura o nível de exposição digital com base em dados públicos em redes sociais,
            transformando sinais qualitativos em métricas acionáveis.
          </p>
        </div>
      </header>

      {/* resumo */}
      <p className="text-[var(--color-foreground)] leading-relaxed">
        O sistema se insere na interseção entre segurança da informação, inteligência artificial e análise de risco cibernético.
        Fornece uma métrica comparável a um "score" para auxiliar decisões de mitigação e conscientização.
      </p>

      {/* grid de cards: objetivos + pontos chave */}
      <div className="grid gap-4 sm:grid-cols-2">
        <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] p-4 shadow-sm">
          <h4 className="text-lg font-semibold text-[var(--color-foreground)]">Objetivos</h4>
          <ul className="mt-3 space-y-2 text-sm text-[var(--color-muted)]">
            <li className="flex items-start gap-3">
              <span className="mt-0.5 text-[var(--color-accent)]">•</span>
              <span>Quantificar o risco associado à superexposição de informações pessoais.</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="mt-0.5 text-[var(--color-accent)]">•</span>
              <span>Conscientizar usuários sobre vulnerabilidades digitais.</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="mt-0.5 text-[var(--color-accent)]">•</span>
              <span>Promover boas práticas de segurança online.</span>
            </li>
          </ul>
        </section>

        <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] p-4 shadow-sm">
          <h4 className="text-lg font-semibold text-[var(--color-foreground)]">Como funciona (resumo)</h4>
          <ol className="mt-3 space-y-2 text-sm text-[var(--color-muted)] list-decimal list-inside">
            <li>Coleta de dados públicos das postagens e metadados.</li>
            <li>Extração de sinais relevantes (p. ex. menção de documentos, localização, saúde).</li>
            <li>Agregação e cálculo do escore com base em impacto e explorabilidade.</li>
          </ol>
        </section>
      </div>

      {/* callout / nota */}
      <div className="rounded-md border-l-4 border-[var(--color-accent)] bg-[var(--color-card)] p-3 text-sm text-[var(--color-muted)]">
        O sistema se insere na interseção entre segurança da informação, inteligência artificial e análise de risco cibernético, propondo uma métrica comparável ao “score de crédito”, mas aplicada à exposição de dados pessoais.
      </div>
    </div>
  )
}