# Arquitetura

O DES foi implementado como um **pipeline modular**, desacoplado em quatro etapas:

## 1) Coleta
- Extração de postagens públicas via API AtProto (Bluesky)
- Execução distribuída (shards / workers)
- Deduplicação e controle de concorrência

## 2) Armazenamento
- Banco orientado a documentos (MongoDB/DocumentDB)
- Estrutura flexível para evolução do schema

## 3) Inferência
- Geração de prompts estruturados por usuário (ou batches)
- Execução em LLM (OpenAI / Bedrock)
- Saída padronizada em JSON com campos booleanos

## 4) Cálculo e visualização
- Pesos derivados de AHP (dois níveis)
- Cálculo do score por usuário
- Agregações (distribuição, categorias, segmentações) para dashboard

## Pastas do repositório
- `apis/`: scripts do pipeline (coleta, inferência, cálculo)
- `exploratory_analysis/`: notebooks/experimentos
- `front-end/`: dashboard e páginas (Next.js)
