export default function MethodCollection() {
  return (
    <div className="space-y-6">

      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] p-4 shadow-sm space-y-3">
        <h4 className="text-lg font-semibold text-[var(--color-foreground)]">De onde vêm os dados</h4>
        <ul className="list-disc list-inside text-sm text-[var(--color-muted)] space-y-2">
          <li>Conteúdo público disponível em redes sociais — coletado de forma ética e conforme termos de uso.</li>
          <li>Foco em postagens e informações públicas de perfis que ajudam a entender padrões de exposição.</li>
        </ul>

        <h4 className="mt-2 text-base font-semibold text-[var(--color-foreground)]">O que coletamos</h4>
        <p className="text-sm text-[var(--color-muted)]">
          Apenas dados que já são visíveis publicamente: textos de postagens e metadados públicos. Não coletamos informações privadas ou protegidas.
        </p>

        <h4 className="mt-2 text-base font-semibold text-[var(--color-foreground)]">Como tratamos esses dados</h4>
        <ul className="list-disc list-inside text-sm text-[var(--color-muted)] space-y-2">
          <li>Análise e limpeza para remover ruído e facilitar a leitura automática.</li>
          <li>Anonimização quando apropriado e minimização dos dados sensíveis.</li>
          <li>Processos documentados para garantir transparência e conformidade com a legislação de privacidade.</li>
        </ul>

        <h4 className="mt-2 text-base font-semibold text-[var(--color-foreground)]">Por que armazenamos</h4>
        <p className="text-sm text-[var(--color-muted)]">
          Armazenamos resultados padronizados para permitir comparação, auditoria e melhoria contínua do método — sempre com controles de acesso e versionamento.
        </p>

        <h4 className="mt-2 text-base font-semibold text-[var(--color-foreground)]">O que isso significa para o usuário</h4>
        <ul className="list-disc list-inside text-sm text-[var(--color-muted)] space-y-1">
          <li>Transparência sobre o que foi analisado.</li>
          <li>Resultados apresentados de forma simples, para informar e educar, não para punir.</li>
          <li>Possibilidade de exportar e revisar os dados resultantes para fins de auditoria.</li>
        </ul>
      </section>
    </div>
  )
}