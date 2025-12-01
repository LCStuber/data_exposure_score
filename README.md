# Data Exposure Score (DES)

O **Data Exposure Score (DES)** é um sistema que mede o nível de **exposição digital** de usuários a partir de dados **manifestamente públicos** em redes sociais.  
Ele combina coleta massiva de postagens, análise com modelos de linguagem (LLMs) e um cálculo de escore inspirado em AHP para transformar exposição de dados em um número de **0 a 1000**, onde:

- `DES = 1000` → nenhuma exposição sensível detectada  
- `DES = 0` → exposição máxima segundo os critérios definidos  

Este repositório contém o código usado no artigo científico **“Data Exposure Score (DES) – Quantificando sua segurança”**, desenvolvido no curso de Ciência da Computação do Instituto Mauá de Tecnologia.

---

## Sumário

- [Visão geral](#visão-geral)
- [Arquitetura em alto nível](#arquitetura-em-alto-nível)
- [Metodologia do escore DES](#metodologia-do-escore-des)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Tecnologias utilizadas](#tecnologias-utilizadas)
- [Como começar](#como-começar)
  - [Ambiente Python](#ambiente-python)
  - [Variáveis de ambiente](#variáveis-de-ambiente)
- [Pipelines de back-end](#pipelines-de-back-end)
- [Dashboard e front-end](#dashboard-e-front-end)
- [Reprodução dos resultados do artigo](#reprodução-dos-resultados-do-artigo)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## Visão geral

O DES foi criado com dois objetivos principais:

1. **Mensurar** o grau de exposição digital de indivíduos com base em suas próprias publicações em redes sociais.
2. **Conscientizar** sobre riscos de autoexposição e incentivar práticas mais seguras de uso das mídias digitais.

No estudo original, utilizamos a rede social **Bluesky** como caso de uso:

- Coleta de ~**92 milhões de postagens** de mais de **500 mil usuários** (≈ 8,19 GB).
- Amostra estatística de **10.000 usuários**, com 95% de confiança e erro máximo de 1% na proporção.

As postagens são analisadas por modelos LLM (como **Llama 3.2 90B Instruct** via Amazon Bedrock e **GPT-4o** via OpenAI), que retornam um **JSON padronizado** com flags booleanas indicando a presença de diferentes tipos de informação sensível. O DES então converte essas flags em um escore numérico de exposição.

---

## Arquitetura em alto nível

A arquitetura do projeto pode ser resumida em quatro etapas principais (pipeline modular):

1. **Coleta de dados**
   - Coleta automatizada de postagens públicas na Bluesky via API aberta **AtProto**.
   - Armazenamento em **Amazon DocumentDB** (compatível com MongoDB), em modo serverless.

2. **Amostragem estatística**
   - Seleção de uma amostra representativa de usuários para análise (10.000 perfis) com base em critérios estatísticos.

3. **Inferência com LLM**
   - Geração de prompts estruturados (com as postagens do usuário).
   - Envio em *batches* para modelos via Amazon Bedrock (Llama 3.2 90B) e API OpenAI (GPT-4o).
   - Recebimento de um JSON padronizado com campos booleanos indicando categorias de exposição (dados de contato, localização, rotina, etc.).

4. **Cálculo do escore DES + visualização**
   - Cálculo do escore ponderado via metodologia AHP em dois níveis.
   - Geração de *dashboards* em **Next.js** com gráficos e recomendações de segurança digital.

Cada etapa é desacoplada: é possível trocar a fonte de dados, o modelo LLM ou o banco sem quebrar o restante do pipeline.

---

## Metodologia do escore DES

O **Data Exposure Score** é calculado em cima de duas ideias:

1. **Quais tipos de dado aparecem** (por exemplo, informação financeira, documentos pessoais, contato, localização, rotina, afiliações, hobbies).
2. **Quão graves e exploráveis** esses dados são em um contexto de segurança da informação.

### Estrutura de ponderação

O DES usa uma estrutura inspirada no **AHP (Analytic Hierarchy Process)** em dois níveis:

- **Nível 1 – Critérios globais**
  - Ex.: **Impacto**, **Explorabilidade**, **Existência**.
- **Nível 2 – Categorias de dados**
  - Ex.: Informação financeira, documentos pessoais, localização em tempo real, contato pessoal, rotina/hábitos, afiliação política/religiosa, hobbies/interesses.

Para cada critério e categoria são atribuídos pesos (ex.: impacto da informação financeira > hobbies). Esses pesos são normalizados para compor um vetor de pesos globais `Wj` por categoria.

### Variáveis e fórmula

Para cada usuário, temos:

- `Vj` = variável de exposição da categoria `j` (neste estudo, **binária**: `1` se o LLM detectou exposição; `0` caso contrário).
- `Wj` = peso global da categoria `j` (resultante do AHP).

1. Primeiro, calculamos um escore intermediário `S` em `[0,1]`:

$$
S = \sum_{j=1}^{n} W_j \cdot V_j
$$

2. Depois, aplicamos a escala **invertida** para o DES:

$$
DES = 1000 \times (1 - S)
$$

- `DES = 1000` → nenhuma exposição detectada.
- `DES = 0` → todas as categorias mais críticas aparecem simultaneamente. 

### Exemplos de ponderação (resumido)

- **Informação financeira**  
  - Impacto: 10 | Explorabilidade: 8  
  - Risco direto de fraude, roubo de identidade, engenharia social direcionada.

- **Hobbies e interesses**  
  - Impacto: 2 | Explorabilidade: 4  
  - Baixo risco isolado, mas útil para criar pretextos críveis em ataques de engenharia social.

Isso garante que expor um salário ou documento pessoal pese muito mais no escore do que citar um hobby.

---

## Estrutura do repositório

```text
data_exposure_score/
├── apis/                  # Scripts de back-end, clients de LLM, pipelines em batch, cálculo do DES
├── exploratory_analysis/  # Notebooks Jupyter e experimentos usados no artigo
├── front-end/             # Dashboard e páginas de documentação (Next.js / TypeScript)
├── requirements.txt       # Dependências Python
├── LICENSE
├── README.md
└── .gitignore
```

A maior parte do projeto está nos **notebooks** (exploration/validação) e scripts Python que compõem o pipeline de coleta, inferência e cálculo do escore.

---

## Tecnologias utilizadas

**Coleta e armazenamento**

* **Bluesky / AtProto** – API aberta para coleta de postagens públicas, respeitando LGPD (dados manifestamente públicos). 
* **Python** – scripts de coleta com paralelismo, *locks* e verificação de duplicidade.
* **Amazon DocumentDB** (compatível com MongoDB) – banco orientado a documentos, modo serverless, escalável. 

**Modelos de linguagem (LLMs)**

* **Llama 3.2 90B Instruct** via **Amazon Bedrock**.
* **GPT-4o** via API **OpenAI**.
* JSON padronizado com flags booleanas por categoria de exposição. 

**Back-end / scripts**

* Python (pipelines, geração de *batches*, chamadas a APIs, gravação em DocumentDB).
* Integrações configuráveis por variáveis de ambiente.

**Front-end**

* **Next.js + TypeScript** – dashboard para visualização do DES e páginas de documentação/metodologia.
* Gráficos para:

  * Distribuição de DES.
  * Comparação entre categorias.
  * Segmentação por faixa etária, sexo etc. 

---

## Como começar

### Ambiente Python

1. **Clonar o repositório**

```bash
git clone https://github.com/LCStuber/data_exposure_score.git
cd data_exposure_score
```

2. **Criar e ativar um ambiente virtual (recomendado)**

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3. **Instalar dependências**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Variáveis de ambiente

Alguns scripts de `apis/` dependem de credenciais e configurações externas. Os nomes exatos podem variar entre os arquivos, mas em geral você vai precisar de algo como:

**Banco (DocumentDB / MongoDB)**

* `MONGODB_URI`
* `MONGODB_DB`
* `MONGODB_COLLECTION_AGGREGATES` (por exemplo, para os agregados do DES)

**OpenAI**

* `OPENAI_API_KEY`

**Gemini (se utilizado em alguma variante)**

* `GEMINI_API_KEY`

**AWS / Bedrock**

* `AWS_ACCESS_KEY_ID`
* `AWS_SECRET_ACCESS_KEY`
* `AWS_REGION`
* `BEDROCK_MODEL_ID` (ex.: modelo Llama 3.2 90B Instruct)

Sugestão: crie um arquivo `.env` na raiz do projeto e use alguma biblioteca de *dotenv* ou mecanismo próprio para carregar essas variáveis antes de rodar os scripts.

---

## Pipelines de back-end

Os scripts em `apis/` implementam o pipeline descrito no artigo. Em linhas gerais:

1. **Coleta e geração de dataset**

   * Scripts para buscar postagens da Bluesky e armazenar no DocumentDB, com controle de concorrência e deduplicação. 

2. **Geração de *batches* e prompts**

   * Agrupamento de usuários e suas postagens em *batches*.
   * Montagem de prompts estruturados com as postagens e instruções para o LLM retornar um JSON padronizado.

3. **Inferência em lote (Bedrock / OpenAI)**

   * Envio dos *batches* para:

     * Bedrock (Llama 3.2 90B Instruct) **ou**
     * OpenAI (GPT-4o).
   * Recebimento, validação e gravação dos JSONs de resposta no DocumentDB. 

4. **Cálculo e agregação do DES**

   * Aplicação das ponderações AHP.
   * Cálculo do `S` e do `DES` por usuário.
   * Criação de coleções agregadas para alimentar dashboards (médias, distribuições, segmentos por faixa etária, sexo, etc.). 

Cada script normalmente expõe um `--help`, por exemplo:

```bash
python apis/<nome_do_script>.py --help
```

Use isso para ver parâmetros de conexão, filtros e opções de limite.

---

## Dashboard e front-end

O diretório `front-end/` contém o código de um dashboard em **Next.js** que:

* Exibe gráficos de distribuição do DES (por faixa, por grupo, por categoria).
* Mostra os principais marcadores de exposição (financeira, documentos, contato, etc.).
* Fornece um contexto educativo, com seções como:

  * Introdução
  * Metodologia (AHP, categorias, pesos)
  * Objetivos e limitações
  * Recomendações práticas de segurança digital 

### Rodando o front-end localmente

Na raiz do repositório:

```bash
cd front-end
npm install        # ou pnpm / yarn, se preferir
npm run dev
```

Depois, acesse o endereço informado no terminal (geralmente `http://localhost:3000`).

> Para visualizar dados reais, configure o front-end para consumir a mesma base que os scripts de back-end populam (por exemplo via API interna ou conexão direta).

---

## Reprodução dos resultados do artigo

Para tentar reproduzir (ou adaptar) os resultados do artigo:

1. **Coleta de dados**

   * Caso você não tenha acesso à mesma base, pode adaptar os scripts para:

     * Coletar dados públicos de outra conta / subconjunto da Bluesky.
     * Utilizar outro conjunto de postagens estruturadas.

2. **Amostragem**

   * Ajuste o tamanho da amostra de acordo com seus recursos de computação.
   * O artigo utiliza uma amostra de **10.000 usuários** com base em fórmula de tamanho de amostra para proporções (95% confiança, erro 1%). 

3. **Inferência com LLM**

   * Teste diferentes modelos (por exemplo, apenas OpenAI ou apenas Bedrock).
   * No artigo, observou-se que:

     * Llama 3.2 90B Instruct → escore médio ≈ **893 (Alto)**.
     * GPT-4o → escore médio ≈ **655 (Médio)**.
       Isso indica que modelos mais robustos tendem a detectar mais exposições, reduzindo falsos negativos. 

4. **Cálculo do DES e dashboards**

   * Execute os scripts de agregação.
   * Utilize o front-end para visualizar as distribuições e comparações entre grupos.

---

## Contribuindo

Contribuições são bem-vindas! Alguns caminhos possíveis:

* **Pesquisa**: testar novas categorias de exposição, métricas ou variações da metodologia AHP.
* **Engenharia**: otimizar pipelines, adicionar novos provedores de LLM, implementar cache, etc.
* **Front-end**: melhorar visualizações, filtros, textos de conscientização e acessibilidade.
* **Privacidade & ética**: sugerir melhorias na forma de comunicação, escopo de dados e aderência a legislações.

Passos sugeridos:

1. Faça um *fork* do repositório.

2. Crie uma *branch* descritiva:

   ```bash
   git checkout -b feature/minha-melhoria
   ```

3. Implemente suas alterações e escreva *commits* claros.

4. Abra um Pull Request explicando:

   * O problema que você resolveu.
   * Como testar.
   * Se alterou dependências, variáveis de ambiente ou contratos de dados.

Autores principais do artigo/projeto:
**Carlos Henrique Lucena Barros, Débora Witkowski, Leonardo Cazotto Stuber, Mateus Capaldo Martins.** 

---

## Licença

Este projeto é licenciado sob os termos da
[GNU General Public License v3.0 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.html).

Consulte o arquivo [`LICENSE`](LICENSE) para mais detalhes.