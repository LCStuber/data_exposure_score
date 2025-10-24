export default function MethodAnalysis() {
  return (
    <div className="space-y-6">

      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] p-4 shadow-sm">
        <h4 className="text-lg font-semibold text-[var(--color-foreground)]">Como analisamos</h4>
        <ul className="mt-3 list-disc list-inside text-sm text-[var(--color-muted)] space-y-2">
          <li>Extraímos informações relevantes dos posts públicos e agrupamos por usuário.</li>
          <li>Usamos métodos automáticos para detectar menções a dados pessoais (nome, localização, documentos, saúde, etc.).</li>
          <li>Sempre que possível, as inferências são validadas por regras simples e por amostras revisadas manualmente.</li>
        </ul>

        <h4 className="mt-4 text-base font-semibold text-[var(--color-foreground)]">Saída</h4>
        <p className="mt-2 text-sm text-[var(--color-muted)]">
          O resultado é um registro padronizado por usuário que indica, de forma clara, quais categorias de informação foram encontradas.
          Essas indicações são pensadas para facilitar interpretação e ações práticas.
        </p>

        <h4 className="mt-4 text-base font-semibold text-[var(--color-foreground)]">Princípios e boas práticas</h4>
        <ul className="mt-2 list-disc list-inside text-sm text-[var(--color-muted)] space-y-1">
          <li>Coleta apenas de conteúdo público e tratamento responsável dos dados.</li>
          <li>Transparência sobre critérios usados para identificar exposição.</li>
          <li>Adoção de auditoria e versão do processo para permitir replicação e melhoria contínua.</li>
          <li>Foco em entregar insights acionáveis, não julgamentos.</li>
        </ul>
      </section>
    </div>
  )
}