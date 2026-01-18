# NOTICE

Este repositório contém a implementação e os artefatos do projeto acadêmico **Data Exposure Score (DES)**, incluindo código, documentação e paper em `paper/`.

## Serviços e dependências de terceiros
O projeto pode integrar (dependendo da execução) serviços e bibliotecas de terceiros, incluindo:

- **Bluesky / AtProto**: utilizado para coleta de postagens públicas via API.
- **Modelos de linguagem (LLMs)**:
  - **OpenAI API** (ex.: GPT-4o), quando configurado.
  - **Amazon Bedrock** (ex.: modelos Llama), quando configurado.
- **Banco de dados**:
  - **MongoDB** e/ou **Amazon DocumentDB** (compatível com MongoDB), quando configurado.
- **Front-end**:
  - **Node.js / npm** e dependências do ecossistema **Next.js**.

O uso desses serviços pode exigir:
- aceitação de **termos de uso** específicos,
- configuração de **credenciais** e chaves de API,
- e pode envolver **custos** (especialmente para inferência em LLM e infraestrutura em nuvem).

## Dados, privacidade e conformidade
- O projeto foi concebido para trabalhar com dados **manifestamente públicos**.
- A execução do pipeline deve respeitar as políticas e termos de uso das plataformas utilizadas e a legislação aplicável (incluindo **LGPD**, quando pertinente).
- Este repositório **não** inclui credenciais, tokens ou bases privadas. Use `.env.example` como referência e **não** faça commit de arquivos `.env`.

## Marcas registradas
Nomes e marcas de serviços citados (por exemplo, Bluesky, OpenAI, Amazon, MongoDB) pertencem a seus respectivos proprietários. O uso aqui é apenas para fins de identificação e interoperabilidade técnica.

## Isenção de responsabilidade
Este projeto é disponibilizado “**no estado em que se encontra**” (“as is”), sem garantias. Os autores não se responsabilizam por usos indevidos, violações de termos de terceiros ou impactos decorrentes de execução fora do escopo acadêmico.
