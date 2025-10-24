import { Italic } from "lucide-react";

export default function IntroSignificado() {
  return (
    <div className="space-y-6">
      <header className="flex items-start gap-4">
        <div className="flex-1 flex items-center justify-center">
          <p className="mt-1 text-sm text-[var(--color-muted)] max-w-xl leading-relaxed text-center">
            A cultura digital contemporânea (cibercultura) aumenta a conectividade e, ao mesmo tempo, a exposição pessoal. Compartilhar traz benefícios, mas reduz a privacidade.
          </p>
        </div>
      </header>

      <div className="text-[var(--color-foreground)] leading-relaxed">
        <p className="mb-3">
          Eventos recentes demonstram o impacto de grandes vazamentos de dados e a necessidade de métricas que avaliem o risco individual:
        </p>

        <ul className="space-y-2 list-inside text-sm text-[var(--color-muted)]">
          <li>
            <strong>“Vazamento do fim do mundo” (2021)</strong> — ~223 milhões de CPFs, endereços e dados bancários expostos.
          </li>
          <li>
            <strong>Incidente MOAB <i>(Mother of All Breaches)</i> (2024)</strong> — mais de 26 bilhões de registros vazados.
          </li>
        </ul>

        <p className="mt-4">
          Mesmo com avanços como <em>Passkeys</em> (FIDO2/WebAuthn) e melhores práticas de criptografia, nada apaga o dano causado por dados já publicados. É preciso medir e educar.
        </p>

        <p className="mt-3">
          O DES surge para preencher essa lacuna: um índice objetivo e didático que quantifica quanto da vida digital de um indivíduo está exposto, permitindo priorizar ações de mitigação e conscientização.
        </p>
      </div>

      <div className="rounded-md border-l-4 border-[var(--color-accent)] bg-[var(--color-card)] p-3 text-sm text-[var(--color-muted)]">
        Nota: o DES é uma ferramenta de avaliação e educação — não substitui análise forense nem ações legais, mas ajuda a priorizar riscos e medidas de proteção.
      </div>
    </div>
  )
}