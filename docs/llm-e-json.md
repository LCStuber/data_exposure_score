# LLM e JSON padronizado

## Por que JSON padronizado?
O pipeline depende de uma saída estruturada para:
- consolidar categorias de exposição de forma consistente
- permitir cálculo direto do score
- suportar replicação em outras plataformas (mantendo o mesmo schema)

## Como funciona
1. Seleciona-se o conjunto de postagens do usuário
2. Monta-se um prompt estruturado
3. O modelo retorna um JSON com campos booleanos por categoria (true/false)
4. O JSON vira entrada do cálculo do DES

## Modelos avaliados
O projeto avaliou modelos diferentes (ex.: OpenAI e um modelo open source via Bedrock).
O paper descreve os impactos dessa escolha no score e nos falsos negativos.
