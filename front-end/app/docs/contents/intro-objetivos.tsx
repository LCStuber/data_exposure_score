export default function IntroObjetivos() {
  return (
    <div className="space-y-6">

      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] p-4 shadow-sm">
        <h4 className="text-lg font-semibold text-[var(--color-foreground)]">Objetivo Geral</h4>
        <p className="mt-2 text-sm text-[var(--color-muted)]">
          Desenvolver e implementar o Data Exposure Score (DES) — um sistema que mede o grau de exposição digital a partir de dados públicos extraídos da rede social Bluesky.
        </p>

        <h5 className="mt-4 font-semibold text-[var(--color-foreground)]">Objetivos Específicos</h5>
        <ul className="mt-2 space-y-2 text-sm text-[var(--color-muted)] list-inside list-disc">
          <li>Integrar fontes públicas de dados respeitando leis de privacidade (LGPD).</li>
          <li>Definir parâmetros para mensurar a exposição digital.</li>
          <li>Utilizar uma LLM para identificar informações sensíveis.</li>
          <li>Construir uma plataforma interativa com visualização dos resultados e impactos.</li>
        </ul>
      </section>
    </div>
  )
}