# Metodologia do Data Exposure Score (DES)

O DES transforma sinais de exposição (variáveis booleanas) em um escore numérico de **0 a 1000**, onde:
- 1000 = nenhuma exposição sensível detectada
- 0 = exposição máxima de acordo com os critérios

## Variáveis
Para cada categoria `j`:
- `Vj`: variável binária de exposição (0/1)
- `Wj`: peso global da categoria (derivado do AHP)

## Fórmula
1) Escore intermediário:
S = Σ (Wj * Vj)

2) Escala invertida:
DES = 1000 * (1 - S)

## AHP em dois níveis
O sistema utiliza uma estrutura hierárquica inspirada no AHP:
- Nível 1: critérios globais (ex.: impacto, explorabilidade, existência)
- Nível 2: categorias de dados (financeiro, documentos, localização, contato, rotina, afiliações, hobbies etc.)

O resultado é um vetor de pesos globais `Wj` que penaliza mais categorias com maior severidade.
