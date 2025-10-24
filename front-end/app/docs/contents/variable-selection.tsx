export default function VariableSelection() {
  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] p-4 shadow-sm">
        <h4 className="text-lg font-semibold text-[var(--color-foreground)]">
          Parâmetros e Ponderação
        </h4>
        <p className="mt-3 text-sm text-[var(--color-muted)]">
          Foi desenvolvido um sistema de pontuação que atribui pesos diferentes
          conforme a explorabilidade e o impacto potencial de cada tipo de
          informação. A estrutura de ponderação (Tabela 2 do
          artigo) constitui o núcleo da lógica de cálculo do DES.
        </p>

        <h4 className="mt-4 text-base font-semibold text-[var(--color-foreground)]">
          Categorias de Risco (Modelo Expandido)
        </h4>
        <ul className="mt-2 list-disc list-inside text-sm text-[var(--color-muted)] space-y-2">
          <li>
            <strong>Informação Financeira:</strong> (Impacto: 10,
            Explorabilidade: 8) Menção a salários, bancos, cartões. Risco
            direto de fraude.
          </li>
          <li>
            <strong>Documentos Pessoais:</strong> (Impacto: 10, Explorabilidade:
            7) Menção a CPF, RG, CNH. Risco crítico de roubo de identidade
           .
          </li>
          <li>
            <strong>Localização em Tempo Real:</strong> (Impacto: 8,
            Explorabilidade: 9) Check-ins, menções a "estou em...". Risco
            iminente de segurança física (stalking).
          </li>
          <li>
            <strong>Contato Pessoal:</strong> (Impacto: 8, Explorabilidade: 10)
            E-mail, número de telefone. Vetor direto para phishing e smishing
           .
          </li>
          <li>
            <strong>Rotina/Hábitos:</strong> (Impacto: 6, Explorabilidade: 6)
            Horários de trabalho, locais frequentados. Permite traçar perfil
            de comportamento.
          </li>
          <li>
            <strong>Afiliação Política/Religiosa:</strong> (Impacto: 4,
            Explorabilidade: 5) Declarações de posicionamento. Risco de
            discriminação e assédio.
          </li>
          <li>
            <strong>Hobbies e Interesses:</strong> (Impacto: 2, Explorabilidade:
            4) Gostos, atividades de lazer. Útil para engenharia social
           .
          </li>
        </ul>

        <h4 className="mt-4 text-base font-semibold text-[var(--color-foreground)]">
          Justificativas de Ponderação
        </h4>
        <ul className="mt-2 list-disc list-inside text-sm text-[var(--color-muted)] space-y-1">
          <li>
            <strong>Dados Sensíveis (LGPD):</strong> Possuem elevada severidade
            ética e jurídica devido ao potencial discriminatório.
          </li>
          <li>
            <strong>Dados de Localização:</strong> Favorecem reidentificação por
            correlação temporal/espacial e implicam riscos físicos.
          </li>
          <li>
            <strong>Mídias Pessoais (Fotos/Vídeos):</strong> Permitem
            reconhecimento facial e exposição acidental de informações
            sigilosas.
          </li>
        </ul>
      </section>
    </div>
  );
}