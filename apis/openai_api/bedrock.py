import os
import logging
import json
import time
import tempfile
import re
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Optional
from bson import ObjectId

import boto3
from botocore.exceptions import ClientError
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


# ENVIRONMENT VARIABLES & GLOBALS


USER = os.getenv("MONGO_USER")
PASS = os.getenv("MONGO_PASS")
HOST = os.getenv("MONGO_HOST")
PORT = os.getenv("MONGO_PORT")
AUTH_DB = os.getenv("MONGO_AUTH_DB")
DB_NAME = os.getenv("MONGO_DB")
COL_DATA = os.getenv("MONGO_COLLECTION_DATA")
COL_REPORT = os.getenv("MONGO_COLLECTION_REPORTS_BEDROCK")

# --- AWS / Bedrock ---
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "qwen.qwen3-32b-v1:0")
BEDROCK_S3_INPUT = os.getenv("BEDROCK_S3_INPUT")   # ex: s3://meu-bucket/bedrock/input/
BEDROCK_S3_OUTPUT = os.getenv("BEDROCK_S3_OUTPUT") # ex: s3://meu-bucket/bedrock/output/
BEDROCK_ROLE_ARN = os.getenv("BEDROCK_ROLE_ARN")   # IAM role para Batch
BEDROCK_BATCH_MIN_RECORDS = int(os.getenv("BEDROCK_BATCH_MIN_RECORDS", "100"))

TLS_CA_FILE = os.getenv("MONGO_TLS_CA_FILE", "rds-combined-ca-bundle.pem")

DEFAULT_BATCH_SIZE = int(os.getenv("BATCH_SIZE", 500))  # linhas por arquivo .jsonl para Batch

# Valida envs essenciais
if not all([USER, PASS, HOST, PORT, AUTH_DB, DB_NAME, COL_DATA, COL_REPORT]):
    raise RuntimeError("Verifique as variáveis de ambiente do Mongo no .env")

if not all([BEDROCK_S3_INPUT, BEDROCK_S3_OUTPUT, BEDROCK_ROLE_ARN]):
    raise RuntimeError("Defina BEDROCK_S3_INPUT, BEDROCK_S3_OUTPUT e BEDROCK_ROLE_ARN no .env")

# MongoDB client
uri = (
    f"mongodb://{HOST}:{PORT}"
    f"/?tls=true&tlsCAFile={TLS_CA_FILE}&replicaSet=rs0&readPreference=secondaryPreferred"
    f"&retryWrites=false&authSource={AUTH_DB}"
)
clientDB = MongoClient(uri, username=USER, password=PASS)
db = clientDB[DB_NAME]
data_coll = db[COL_DATA]
reports_coll = db[COL_REPORT]

def ensure_indexes():
    try:
        reports_coll.create_index("source_id", unique=True)
    except Exception as e:
        print(f"[WARN] create_index(reports.source_id) ignorado: {e}")
    try:
        data_coll.create_index([("significant", 1), ("report_id", 1), ("report_id_bedrock", 1)])
    except Exception as e:
        print(f"[WARN] create_index(data.significant, report_id) ignorado: {e}")

ensure_indexes()


# AWS clients

bedrock_ctl = boto3.client("bedrock", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)


# QWEN3 / Prompt helpers


CAMPO_LIST = (
    "NomeDeclaradoOuSugeridoPeloAutor",
    "IdadeDeclaradaOuInferidaDoAutor",
    "GeneroAutoDeclaradoOuInferidoDoAutor",
    "OrientacaoSexualDeclaradaOuSugeridaPeloAutor",
    "StatusDeRelacionamentoDeclaradoOuSugeridoPeloAutor",
    "ProfissaoOcupacaoDeclaradaPeloAutor",
    "NivelEducacionalDeclaradoOuInferidoPeloAutor",
    "LocalizacaoPrincipalDeclaradaOuInferidaDoAutor",
    "CidadesComRelevanciaPessoalParaOAutor",
    "CrencaReligiosaDeclaradaOuSugeridaPeloAutor",
    "OpinioesPoliticasExpressasPeloAutor",
    "ExposicaoDeRelacionamentosPessoaisPeloAutor",
    "MencaoDoAutorAPosseDeCPF",
    "MencaoDoAutorAPosseDeRG",
    "MencaoDoAutorAPosseDePassaporte",
    "MencaoDoAutorAPosseDeTituloEleitor",
    "EtniaOuRacaAutoDeclaradaPeloAutor",
    "MencaoDoAutorAEnderecoResidencial",
    "MencaoDoAutorAContatoPessoal_TelefoneEmail",
    "MencaoDoAutorADadosBancarios",
    "MencaoDoAutorACartaoDeEmbarque",
    "IndicadoresDeRendaPropriaMencionadosPeloAutor",
    "MencoesAPatrimonioPessoalDoAutor",
    "LocalDeTrabalhoOuEstudoDeclaradoPeloAutor",
    "MencaoDoAutorARecebimentoDeBeneficioSocial",
    "MencoesAoProprioHistoricoFinanceiroPeloAutor",
    "MencoesDoAutorAProprioHistoricoCriminal",
    "MencaoDoAutorAPosseDeChavePix"
)

def build_prompt(tweets_json: str) -> str:
    return (
        "Você é um analista de perfis do Twitter/BlueSky.\n"
        "Analise os tweets e RETORNE ESTRITAMENTE um JSON válido, sem markdown e sem comentários.\n"
        "Formato:\n"
        "{\n"
        '  "InformacoesIniciais": { <TODOS os CAMPOS abaixo com valores "VERDADEIRO" ou "FALSO"> },\n'
        '  "InformacoesAdicionais": { "Idade": <numero apenas ou null>, "Genero": <masculino, feminino, ou outros ou null>, "DataUltimoTweet": <ISO8601 ou null> }\n'
        "}\n"
        f"CAMPOS: {CAMPO_LIST}.\n"
        f"TWEETS: {tweets_json}"
    )

def choose_posts(posts: List[Dict], max_posts: int = 80, max_chars: int = 8000) -> List[Dict]:
    def parse_ts(p):
        ts = p.get("created_at")
        if not ts:
            return datetime.min.replace(tzinfo=timezone.utc)
        try:
            if ts.endswith("Z"):
                ts = ts.replace("Z", "+00:00")
            return datetime.fromisoformat(ts)
        except Exception:
            return datetime.min.replace(tzinfo=timezone.utc)

    pts = [p for p in posts if p.get("lang") == "pt"]
    pts.sort(key=parse_ts, reverse=True)
    out, total = [], 0
    for p in pts[:max_posts]:
        s = json.dumps(p, ensure_ascii=False)
        if total + len(s) > max_chars:
            break
        out.append(p)
        total += len(s)
    return out

def extract_json(text: str) -> Optional[Dict]:
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S | re.I)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"(\{.*\})", text, flags=re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    return None

def _normalize_response_body(raw):
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", errors="replace")
    if isinstance(raw, str):
        raw_str = raw.strip()
        try:
            parsed = json.loads(raw_str)
            if isinstance(parsed, str):
                try:
                    parsed2 = json.loads(parsed)
                    return parsed2
                except Exception:
                    return parsed
            return parsed
        except Exception:
            return raw_str
    return raw

def extract_text_from_response(resposta_body):
    """
    Aceita a estrutura de saída do Bedrock (modelOutput do Batch), que por sua vez
    é idêntica ao corpo retornado pelo InvokeModel do provedor.
    Tenta extrair texto de formatos OpenAI-like (choices[0].message.content) ou
    Titan-like (results[0].outputText). Fallback: serializa o corpo inteiro.
    """
    try:
        body = _normalize_response_body(resposta_body)
        if isinstance(body, str):
            return body
        if isinstance(body, dict):
            # OpenAI-like
            if "choices" in body and isinstance(body["choices"], list) and body["choices"]:
                choice = body["choices"][0]
                if isinstance(choice, dict):
                    if "message" in choice and isinstance(choice["message"], dict) and "content" in choice["message"]:
                        return str(choice["message"]["content"]).strip()
                    if "text" in choice:
                        return str(choice["text"]).strip()
                    if "delta" in choice:
                        return json.dumps(choice["delta"], ensure_ascii=False)
            # Titan-like
            if "results" in body and isinstance(body["results"], list) and body["results"]:
                first = body["results"][0]
                if isinstance(first, dict) and "outputText" in first:
                    return str(first["outputText"]).strip()
            # Erro padronizado?
            if "error" in body:
                try:
                    return "__API_ERROR__ " + json.dumps(body["error"], ensure_ascii=False)
                except Exception:
                    return "__API_ERROR__ " + str(body["error"])
            # Outros campos comuns
            for possible in ("output", "data", "result"):
                if possible in body:
                    return json.dumps(body[possible], ensure_ascii=False)
            return json.dumps(body, ensure_ascii=False)
        return str(body)
    except Exception as e:
        logging.exception("Erro extraindo texto da resposta")
        return f"__PARSE_EXCEPTION__ {e} | raw={repr(resposta_body)}"


# S3 helpers


def _parse_s3_uri(s3_uri: str):
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"URI inválida: {s3_uri}")
    path = s3_uri[5:]
    bucket, _, prefix = path.partition("/")
    return bucket, prefix

def s3_upload_text(s3_uri: str, text: str):
    bucket, prefix = _parse_s3_uri(s3_uri)
    if not prefix or prefix.endswith("/"):
        raise ValueError("Forneça uma chave completa (incluindo nome do arquivo) para upload no S3.")
    s3.put_object(Bucket=bucket, Key=prefix, Body=text.encode("utf-8"))

def s3_list_prefix(s3_uri_prefix: str):
    bucket, prefix = _parse_s3_uri(s3_uri_prefix)
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            yield bucket, obj["Key"]

def s3_iter_lines(bucket: str, key: str):
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"]
    for raw in body.iter_lines():
        if not raw:
            continue
        if isinstance(raw, (bytes, bytearray)):
            line = raw.decode("utf-8")
        else:
            line = str(raw)
        yield line.strip()


# Batch line builder (Bedrock)


def qwen_model_input_from_doc(doc: Dict) -> Optional[Dict]:
    """
    Constrói o 'modelInput' para o Bedrock (InvokeModel) no formato OpenAI-like
    aceito pelos modelos Qwen3 no Bedrock (messages + max_tokens/temperature).
    """
    source_id = str(doc["_id"])
    tweets_pt = choose_posts(doc.get("posts", []))
    if not tweets_pt:
        return None

    tweets_json = json.dumps(tweets_pt, ensure_ascii=False)
    prompt = build_prompt(tweets_json)

    # messages: system + user
    messages = [
        {"role": "system", "content": "Analista de perfis de BlueSky"},
        {"role": "user", "content": prompt}
    ]

    # Corpo aceito pelo InvokeModel para Qwen3 (OpenAI-like)
    body = {
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.2,
        "top_p": 0.9
    }
    return {"recordId": source_id, "modelInput": body}

def write_jsonl_records(records: List[Dict]) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl", mode="w", encoding="utf-8")
    for rec in records:
        tmp.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp.close()
    return tmp.name


# Processamento de resultados (S3 -> Mongo)


def processar_resultados_desde_output_prefix(output_prefix_uri: str):
    """
    Lê todos os .jsonl sob o prefixo de saída do job e insere/atualiza no Mongo.
    Espera o formato:
      { "recordId": "id", "modelInput": {...}, "modelOutput": {...} }
    ou com "error" no lugar de "modelOutput".
    """
    processed = 0
    for bucket, key in s3_list_prefix(output_prefix_uri):
        if not key.endswith(".jsonl") or key.endswith("manifest.json.out"):
            continue
        for line in s3_iter_lines(bucket, key):
            try:
                registro = json.loads(line)
            except Exception:
                print(f"[WARN] Linha inválida no output: {line[:200]}...")
                continue

            source_id = registro.get("recordId")
            if not source_id:
                # fallback: tenta encontrar no input
                source_id = (registro.get("modelInput") or {}).get("custom_id")

            if "error" in registro:
                logging.error("Erro no registro %s: %s", source_id, registro["error"])
                relatorio_raw = "__API_ERROR__ " + json.dumps(registro["error"], ensure_ascii=False)
            else:
                model_output = registro.get("modelOutput", {})
                relatorio_raw = extract_text_from_response(model_output)

            relatorio_dict = extract_json(relatorio_raw)

            try:
                doc_to_insert = {
                    "source_id": source_id,
                    "report": relatorio_dict if relatorio_dict is not None else relatorio_raw,
                    "parse_ok": relatorio_dict is not None,
                    "analyzed_at": datetime.now(timezone.utc),
                }
                res_upsert = reports_coll.update_one(
                    {"source_id": source_id},
                    {"$setOnInsert": doc_to_insert},
                    upsert=True
                )
                inserted_id = (
                    res_upsert.upserted_id
                    if res_upsert.upserted_id is not None
                    else reports_coll.find_one({"source_id": source_id}, {"_id": 1})["_id"]
                )

                data_coll.update_one(
                    {"_id": ObjectId(source_id), "report_id_bedrock": {"$exists": False}},
                    {"$set": {"report_id_bedrock": inserted_id}}
                )

                processed += 1
                if processed % 50 == 0:
                    print(f"[OK] Processados {processed} reports...")
            except Exception as e:
                print(f"[ERRO] Falha ao salvar relatório/atualizar doc {source_id}: {e}")

    print(f"[INFO] Total processado: {processed}")


# Pipeline principal (Bedrock Batch)


def processar_bsky_docs(max_docs: Optional[int] = None):
    """
    Cria lotes (.jsonl) para o Amazon Bedrock Batch Inference e aguarda finalizar,
    processando os outputs do S3. Evita cursores abertos no Mongo.
    """
    filtro_base = {"significant": True, "report_id": {"$exists": True}, "report_id_bedrock": {"$exists": False}}

    try:
        total = data_coll.count_documents(filtro_base)
        print(f"[INFO] Pendente em `{COL_DATA}`: {total} documentos (sem report_id)")
    except Exception as e:
        print(f"[WARN] count_documents falhou/foi lento, seguindo sem: {e}")

    total_enfileirados = 0

    while True:
        restante = (max_docs - total_enfileirados) if max_docs is not None else None
        if restante is not None and restante <= 0:
            break

        fetch_n = min(DEFAULT_BATCH_SIZE, restante) if restante is not None else DEFAULT_BATCH_SIZE
        docs = list(
            data_coll.find(filtro_base, projection={"posts": 1})
                     .limit(fetch_n)
        )
        if not docs:
            break

        records: List[Dict] = []
        since_batch = time.perf_counter()

        for doc in docs:
            rec = qwen_model_input_from_doc(doc)
            if rec:
                records.append(rec)

        if not records:
            continue

        elapsed = time.perf_counter() - since_batch
        print(f"[INFO] Fechando batch de {len(records)} reqs (acumuladas: {total_enfileirados + len(records)}) | +{elapsed:.1f}s")

        # Respeita o mínimo típico de registros por job (p. ex. 100)
        if len(records) < BEDROCK_BATCH_MIN_RECORDS:
            print(f"[WARN] Registros no lote ({len(records)}) < mínimo recomendado ({BEDROCK_BATCH_MIN_RECORDS}). O job pode falhar por cota mínima.")
        execute_batch(records)

        total_enfileirados += len(records)

    print(f"[INFO] Finalizado. Contas enfileiradas para análise: {total_enfileirados}{'' if max_docs is None else f' / alvo {max_docs}'}")

def execute_batch(records: List[Dict]):
    """
    1) Escreve .jsonl local
    2) Upload para S3 input (chave única por job)
    3) Cria job no Bedrock
    4) Aguarda completar
    5) Processa resultados lendo S3 output
    """
    print(f"[INFO] Preparando batch com {len(records)} registros...")

    # 1) arquivo .jsonl temporário
    jsonl_path = write_jsonl_records(records)

    # 2) upload para S3 input com chave única
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    job_name = f"twitter-bsky-script-{ts}"
    input_bucket, input_prefix_base = _parse_s3_uri(BEDROCK_S3_INPUT.rstrip("/") + "/")
    input_key = f"{input_prefix_base}{job_name}/input.jsonl"
    with open(jsonl_path, "r", encoding="utf-8") as fh:
        s3.put_object(Bucket=input_bucket, Key=input_key, Body=fh.read().encode("utf-8"))
    try:
        os.unlink(jsonl_path)
    except Exception:
        pass
    input_uri = f"s3://{input_bucket}/{input_key}"

    # 3) define output prefix único por job
    out_bucket, out_prefix_base = _parse_s3_uri(BEDROCK_S3_OUTPUT.rstrip("/") + "/")
    output_prefix = f"{out_prefix_base}{job_name}/"
    output_uri = f"s3://{out_bucket}/{output_prefix}"

    print(f"[INFO] Enviando job Batch: {job_name}")
    inputDataConfig = {"s3InputDataConfig": {"s3Uri": input_uri}}
    outputDataConfig = {"s3OutputDataConfig": {"s3Uri": output_uri}}

    try:
        resp = bedrock_ctl.create_model_invocation_job(
            roleArn=BEDROCK_ROLE_ARN,
            modelId=BEDROCK_MODEL_ID,
            jobName=job_name,
            inputDataConfig=inputDataConfig,
            outputDataConfig=outputDataConfig,
        )
    except ClientError as e:
        raise RuntimeError(f"Falha ao criar batch no Bedrock: {e}")

    job_arn = resp.get("jobArn")
    print(f"    Job ARN: {job_arn}")

    # 4) aguarda conclusão
    wait_bedrock_job(job_arn, poll_seconds=60)

    # 5) processa resultados
    processar_resultados_desde_output_prefix(output_uri)

def wait_bedrock_job(job_identifier: str, poll_seconds: int = 60):
    print(f"[INFO] Aguardando conclusão do job {job_identifier}...")
    last_status = None
    while True:
        info = bedrock_ctl.get_model_invocation_job(jobIdentifier=job_identifier)
        status = info.get("status")
        if status != last_status:
            counts = info.get("validationMetrics") or {}
            print(f"    status: {status} | info: {counts}")
            last_status = status
        if status in {"Completed", "Failed", "Expired", "Stopped"}:
            if status != "Completed":
                print(f"[ERRO] Job terminou com status {status}")
            return info
        time.sleep(poll_seconds)


def main():
    parser = argparse.ArgumentParser(description="Processa contas e gera relatórios via Amazon Bedrock Batch (Qwen3-32B).")
    parser.add_argument("-n", "--num", type=int, default=None,
                        help="Número MÁXIMO de contas a analisar (default: ilimitado)")
    parser.add_argument("--batch-size", type=int, default=None,
                        help="Sobrescreve o batch size (linhas por arquivo .jsonl)")
    args = parser.parse_args()

    global DEFAULT_BATCH_SIZE
    if args.batch_size is not None and args.batch_size > 0:
        DEFAULT_BATCH_SIZE = args.batch_size
        print(f"[INFO] Batch size sobrescrito para {DEFAULT_BATCH_SIZE}")

    if args.num is not None and args.num <= 0:
        print("[INFO] Nada a fazer: --num <= 0")
        return

    print(f"[INFO] Iniciando pipeline (Bedrock/Qwen3-32B). Limite de contas: {args.num if args.num is not None else 'ilimitado'}")
    processar_bsky_docs(max_docs=args.num)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[INFO] Execução interrompida pelo usuário.")
