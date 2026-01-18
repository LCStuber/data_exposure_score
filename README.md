# Data Exposure Score (DES)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18293679.svg)](https://doi.org/10.5281/zenodo.18293679)

**DOI (Zenodo):** 10.5281/zenodo.18293679  
**Release (TCC):** `1.0.0-tcc`

O **Data Exposure Score (DES)** é um sistema que **mensura a exposição digital** de indivíduos a partir de dados **manifestamente públicos** compartilhados em redes sociais. Ele combina **coleta em larga escala**, **análise com modelos de linguagem (LLMs)** e um **cálculo ponderado inspirado em AHP** para gerar um escore de **0 a 1000**, onde:

- `DES = 1000` → nenhuma exposição sensível detectada  
- `DES = 0` → exposição máxima (segundo os critérios/pesos adotados)

Este repositório contém os artefatos do trabalho **“Data Exposure Score (DES) – Quantificando sua segurança”** (TCC / artigo científico – Instituto Mauá de Tecnologia).

## Links rápidos
- 📄 Paper (PDF): `paper/DES-Artigo.pdf`
- 📚 Documentação: `docs/index.md`
- 🧾 Citação: `CITATION.cff`
- 🖥️ Dashboard (Next.js): `front-end/`
- 📦 Código do pipeline: `apis/`
- 🧪 Notebooks / análises: `exploratory_analysis/`

---

## Sumário
- [Visão geral](#visão-geral)
- [Como o DES funciona](#como-o-des-funciona)
  - [1) Coleta](#1-coleta)
  - [2) Amostragem estatística](#2-amostragem-estatística)
  - [3) Inferência com LLM + JSON padronizado](#3-inferência-com-llm--json-padronizado)
  - [4) Cálculo do escore (AHP)](#4-cálculo-do-escore-ahp)
- [Resultados reportados no paper](#resultados-reportados-no-paper)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Instalação e execução](#instalação-e-execução)
  - [Back-end (Python)](#back-end-python)
  - [Front-end (Next.js)](#front-end-nextjs)
- [Reprodutibilidade](#reprodutibilidade)
- [Ética, privacidade e LGPD](#ética-privacidade-e-lgpd)
- [Como citar](#como-citar)
- [Licença](#licença)
- [Créditos](#créditos)

---

## Visão geral
A exposição digital frequentemente acontece de forma **inconsciente**: menções a rotina, localização, contatos, documentos e informações financeiras podem ampliar a superfície de ataque para **engenharia social**, **phishing** e outras ameaças.

O DES foi desenvolvido para:
- **Quantificar** a exposição individual em um valor numérico interpretável (similar a um “score”).
- **Identificar** categorias de exposição a partir de texto (postagens).
- **Conscientizar** e apoiar educação digital e segurança da informação.
- Ser **replicável**: a metodologia pode ser adaptada para outras plataformas desde que os dados textuais possam ser coletados e analisados por LLM.

---

## Como o DES funciona
O DES é um pipeline modular com quatro etapas principais.

### 1) Coleta
- Fonte do estudo: **Bluesky**, escolhida por oferecer **API aberta (AtProto)** e viabilizar coleta ética de conteúdos públicos.
- Execução distribuída com múltiplas instâncias e controle de concorrência (locks), deduplicação e “sharding”.
- Armazenamento em banco orientado a documentos (**Amazon DocumentDB / MongoDB compatível**).

### 2) Amostragem estatística
Como a base coletada é muito grande, o estudo define uma amostra representativa para análise estatística.
- Confiança: **95%**
- Margem de erro: **1% na proporção**
- Resultado arredondado para **10.000 usuários**.

### 3) Inferência com LLM + JSON padronizado
Cada usuário é analisado a partir de suas postagens públicas:
1. As postagens são agrupadas em **batches**.
2. Um **prompt estruturado** instrui o modelo a retornar um **JSON padronizado**.
3. O JSON contém **valores booleanos** indicando presença/ausência de categorias de exposição (ex.: contato, finanças, documentos, localização, rotina, afiliações, hobbies etc.).
4. Os resultados são persistidos no banco, vinculados ao identificador do usuário.

O pipeline foi implementado para integrar **múltiplos provedores**:
- **Amazon Bedrock** (ex.: Llama 3.2 90B Instruct)
- **OpenAI API** (ex.: GPT-4o)

### 4) Cálculo do escore (AHP)
O DES usa uma estrutura inspirada no **AHP (Analytic Hierarchy Process)** para atribuir pesos e transformar exposição em escore.

- Critérios globais (nível 1): exemplo — **Impacto**, **Explorabilidade**, **Existência**
- Categorias (nível 2): ex.: informação financeira, documentos pessoais, localização, contato, rotina/hábitos, afiliações, hobbies.

**Variáveis**
- `Vj` = variável de exposição da categoria `j` (binária: 0/1, a partir do JSON do LLM)
- `Wj` = peso global da categoria `j` (derivado do AHP)

**Fórmula**
- Escore intermediário: `S = Σ (Wj · Vj)` com `S ∈ [0,1]`
- Escala final invertida: `DES = 1000 · (1 - S)`

---

## Resultados reportados no paper
Resumo do que foi observado no estudo (detalhes no PDF em `paper/`):

- Coleta em larga escala na Bluesky (dezenas de milhões de postagens; centenas de milhares de usuários).
- A amostra final do experimento: **10.000 usuários**.
- O desempenho e o “rigor” do score variam conforme o modelo:
  - Um modelo menos sensível pode gerar **falsos negativos** e aumentar artificialmente o DES (sensação falsa de segurança).
  - Um modelo mais robusto tende a detectar mais exposições e produzir um score mais conservador.

---

## Estrutura do repositório
```text
data_exposure_score/
├── apis/                  # Pipeline: coleta, batches, inferência, cálculo e agregações
├── exploratory_analysis/  # Notebooks/experimentos usados no estudo
├── front-end/             # Dashboard em Next.js / TypeScript
├── docs/                  # Documentação em Markdown (guia do projeto)
├── paper/                 # Artigo científico (PDF/DOCX)
├── requirements.txt       # Dependências Python
├── .env.example           # Exemplo de variáveis de ambiente
├── CITATION.cff           # Metadados de citação (GitHub/Zenodo)
├── LICENSE
└── README.md
```

---

## Instalação e execução

### Back-end (Python)

1. Clone:

```bash
git clone https://github.com/LCStuber/data_exposure_score.git
cd data_exposure_score
```

2. Ambiente virtual:

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3. Dependências:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Variáveis de ambiente:

* Crie o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

* Preencha com suas credenciais (Bluesky, Mongo/DocumentDB, OpenAI/AWS etc.).

5. Execução dos scripts:
   Como o pipeline é composto por múltiplos scripts, use:

```bash
python apis/<script>.py --help
```

e execute por etapas (coleta → inferência → cálculo → agregações).

> Observação: a execução completa depende de credenciais e pode envolver custos de inferência.

### Front-end (Next.js)

```bash
cd front-end
npm install
npm run dev
```

Acesse a URL exibida no terminal (geralmente `http://localhost:3000`).

---

## Reprodutibilidade

* **Reprodução completa** do experimento do paper requer acesso a serviços externos (API Bluesky, banco, endpoints de inferência).
* Para **reprodução parcial**, você pode:

  * executar trechos do pipeline com um conjunto reduzido de dados
  * usar os notebooks de análise em `exploratory_analysis/`
  * validar a metodologia (JSON → AHP → score) com amostras menores

---

## Ética, privacidade e LGPD

* O projeto trabalha com dados **manifestamente públicos**.
* O foco é **estatístico/educacional**: identificar padrões e quantificar exposição, não rastrear indivíduos.
* A escolha do caso de estudo (Bluesky + API aberta) foi feita para manter **conformidade** e transparência.

---

## Como citar

Use o DOI do Zenodo e/ou o arquivo `CITATION.cff`.

**BibTeX (exemplo)**

```bibtex
@software{stuber_data_exposure_score_des,
  title   = {Data Exposure Score (DES) - Quantificando sua seguranca},
  author  = {Stuber, Leonardo Cazotto and Barros, Carlos Henrique Lucena and Martins, Mateus Capaldo and Witkowski, Debora and Serra, Ana Paula Goncalves and Alvarenga, Milkes Yone},
  doi     = {10.5281/zenodo.18293679},
  url     = {https://doi.org/10.5281/zenodo.18293679},
  version = {1.0.0-tcc}
}
```

---

## Licença

Este projeto é licenciado sob **GNU GPL-3.0**. Veja `LICENSE`.

---

## Créditos

Autores:

* Leonardo Cazotto Stuber
* Carlos Henrique Lucena Barros
* Mateus Capaldo Martins
* Débora Witkowski

Orientadoras:

* Profa. Dra. Ana Paula Gonçalves Serra
* Profa. Dra. Milkes Yone Alvarenga
