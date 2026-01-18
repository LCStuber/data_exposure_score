# Data Exposure Score (DES) — Documentação

Esta documentação descreve o **Data Exposure Score (DES)**: um sistema que quantifica o nível de exposição digital de usuários em redes sociais a partir de dados **manifestamente públicos**.

## Links rápidos
- Paper (PDF): `../paper/DES-Artigo.pdf`
- Código: [raiz do repositório](https://github.com/LCStuber/data_exposure_score/)
- DOI (Zenodo): `10.5281/zenodo.18293679`
- Como citar: `../CITATION.cff`

## Conteúdo
- [Arquitetura](arquitetura.md)
- [Metodologia do DES (AHP)](metodologia.md)
- [Dados e amostragem](dados-e-amostragem.md)
- [LLM + JSON padronizado](llm-e-json.md)
- [Reprodutibilidade](reproducibilidade.md)
- [Ética e LGPD](etica-e-lgpd.md)

## Visão geral do pipeline
1. Coleta de dados (Bluesky / AtProto)
2. Amostragem estatística
3. Inferência com LLM (preenchimento de JSON booleano)
4. Cálculo do DES + agregações + dashboard
