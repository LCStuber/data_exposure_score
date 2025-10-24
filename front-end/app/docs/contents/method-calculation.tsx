'use client'

import React from 'react'
import { SiLatex } from 'react-icons/si'

export default function MethodCalculation(): JSX.Element {
  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] p-4 shadow-sm">
        <h4 className="text-lg font-semibold text-[var(--color-foreground)]">
          Como analisamos (Pipeline de Dados)
        </h4>

        <ul className="mt-3 list-disc list-inside text-sm text-[var(--color-muted)] space-y-2">
          <li>
            Os dados públicos são extraídos da rede social Bluesky via API aberta
            (AtProto) usando scripts Python.
          </li>
          <li>
            As postagens e metadados são armazenados em um banco de dados
            orientado a documentos (Amazon DocumentDB).
          </li>
          <li>
            Um modelo de linguagem open source (meta-llama/Llama-2-13b-hf)
            analisa as postagens.
          </li>
          <li>
            O modelo retorna um JSON padronizado com valores booleanos
            (VERDADEIRO/FALSO) indicando a presença de informações pessoais.
          </li>
          <li>
            O escore DES é calculado com base nas informações identificadas
            pelo modelo.
          </li>
        </ul>

        <h4 className="mt-4 text-base font-semibold text-[var(--color-foreground)]">
          Cálculo do Escore (A Fórmula)
        </h4>
        <p className="mt-2 text-sm text-[var(--color-muted)]">
          O escore quantifica o nível de exposição. O cálculo
          considera três dimensões principais: Existência, Impacto e
          Explorabilidade.
        </p>

        <div className="mt-3 rounded-md bg-[var(--color-bg-inset)] p-3 text-sm text-[var(--color-muted)]">
          <p className="flex items-center gap-2 font-mono">
            <SiLatex size={18} className="text-[var(--color-icon)]" aria-hidden />
            <span>
              DES = Σ<sub>i=1</sub><sup>n</sup> (I<sub>i</sub> × E<sub>i</sub> × V<sub>i</sub>)
            </span>          </p>

          <ul className="mt-3 list-disc list-inside space-y-1 pl-2">
            <li>
              <strong>n</strong>: Número total de parâmetros (categorias)
              analisados.
            </li>
            <li>
              <strong>I<sub>i</sub></strong>: Impacto (criticidade) causado pela
              divulgação da categoria <em>i</em>.
            </li>
            <li>
              <strong>E<sub>i</sub></strong>: Explorabilidade estimada da categoria <em>i</em>.
            </li>
            <li>
              <strong>V<sub>i</sub></strong>: Valor da categoria <em>i</em> (1 se VERDADEIRO,
              0 se FALSO).
            </li>
          </ul>
        </div>
      </section>
    </div>
  )
}
