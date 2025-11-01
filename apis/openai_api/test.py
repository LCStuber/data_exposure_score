# test_bedrock_10_accounts.py
import os
import json
from datetime import datetime, timedelta
from aggregate_reports import process_reports_from_iterable, summarize_aggregation_with_qwen

# Opcional: defina essas vars no seu terminal antes de rodar (exemplo):
# export BEDROCK_MODEL_ID="qwen3-32b"
# export AWS_REGION="us-east-1"
# export AWS_BEARER_TOKEN_BEDROCK="eyJhbGciOiJ..."   # se for usar bearer token

# --- cria 10 documentos de teste com variação ---
base_date = datetime(2023, 1, 10)
docs = []
for i in range(10):
    # rotaciona meses e idades/gêneros
    dt = (base_date + timedelta(days=30 * (i % 6))).isoformat() + "Z"
    age = 18 + (i * 4) % 60
    gender = ["Masculino", "Feminino", "nb"][i % 3]
    iniciais = {}
    # marca alguns campos como expostos para variar o DES
    if i % 2 == 0:
        iniciais["MencaoDoAutorAPosseDeCPF"] = "VERDADEIRO"
    if i % 3 == 0:
        iniciais["MencaoDoAutorADadosBancarios"] = "VERDADEIRO"
    if i % 4 == 0:
        iniciais["NomeDeclaradoOuSugeridoPeloAutor"] = "VERDADEIRO"
    if i % 5 == 0:
        iniciais["MencaoDoAutorAContatoPessoal_TelefoneEmail"] = "VERDADEIRO"

    doc = {
        "report": {
            "InformacoesIniciais": iniciais,
            "InformacoesAdicionais": {
                "Idade": age,
                "Genero": gender,
                "DataUltimoTweet": dt
            }
        }
    }
    docs.append(doc)

# --- processa os documentos ---
agg = process_reports_from_iterable(docs)

print("=== AGGREGATION RESULT (summary) ===")
print(json.dumps(agg, ensure_ascii=False, indent=2))

# --- opcional: chama Bedrock/Qwen3 para gerar um resumo ---
# Certifique-se de ter definido BEDROCK_MODEL_ID e credenciais (AWS_BEARER_TOKEN_BEDROCK ou boto3 creds)
try:
    print("\n=== CHAMANDO Bedrock/Qwen3 para resumo (se configurado) ===")
    summarize_aggregation_with_qwen(agg)
except Exception as e:
    print(f"[WARN] Falha na chamada ao Bedrock (verifique credenciais/vars): {e}")
