# Reprodutibilidade

## Pré-requisitos
- Python 3.x + `requirements.txt`
- Acesso às credenciais (Bluesky, Mongo/DocumentDB, OpenAI/AWS etc.)
- `.env` configurado (use `.env.example`)

## Execução (alto nível)
Como os scripts variam por arquivo, a recomendação é:
- verificar `--help` em cada script de `apis/`
- executar por etapas (coleta → inferência → cálculo → agregações)

Exemplo:
python apis/<script>.py --help

## Limitações
A reprodução completa depende de:
- disponibilidade e limites de API
- custos de inferência em LLM
- restrições legais (LGPD) e de acesso a dados

## Replicação para outras redes
O paper discute que a arquitetura modular permite adaptar a metodologia desde que:
- seja possível coletar dados textuais
- o JSON padronizado seja mantido como interface de saída do LLM
