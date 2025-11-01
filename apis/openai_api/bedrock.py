import os
import logging
import json
import time
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


# ENVIRONMENT VARIABLES


USER = os.getenv("MONGO_USER")
PASS = os.getenv("MONGO_PASS")
HOST = os.getenv("MONGO_HOST")
PORT = os.getenv("MONGO_PORT")
AUTH_DB = os.getenv("MONGO_AUTH_DB")
DB_NAME = os.getenv("MONGO_DB")
COL_DATA = os.getenv("MONGO_COLLECTION_DATA")
COL_REPORT = os.getenv("MONGO_COLLECTION_REPORTS_BEDROCK")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Use o FOUNDATION MODEL (sem 'us.'/'global.')
# Haiku 3:
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-2-90b-instruct-v1:0")

TLS_CA_FILE = os.getenv("MONGO_TLS_CA_FILE", "rds-combined-ca-bundle.pem")

# Quantos docs buscar por iteração (não é batch, só paginação local)
DEFAULT_PAGE_SIZE = int(os.getenv("PAGE_SIZE", 200))

# Valida envs essenciais (Mongo)
if not all([USER, PASS, HOST, PORT, AUTH_DB, DB_NAME, COL_DATA, COL_REPORT]):
    raise RuntimeError("Verifique as variáveis de ambiente do Mongo no .env")


# MongoDB


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


# AWS Bedrock Runtime


bedrock_rt = boto3.client("bedrock-runtime", region_name=AWS_REGION)


# Prompt helpers


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
            if isinstance(ts, str) and ts.endswith("Z"):
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
        m2 = re.search(r"(\{.*\})", text, flags=re.S)
        if m2:
            try:
                return json.loads(m2.group(1))
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
                # caso venha string JSON dentro de string
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
    try:
        body = _normalize_response_body(resposta_body)
        if isinstance(body, str):
            return body

        if isinstance(body, dict):
            # Anthropic messages (já ok)
            if "content" in body and isinstance(body["content"], list):
                texts = []
                for item in body["content"]:
                    if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                        texts.append(str(item["text"]))
                if texts:
                    return "\n".join(texts).strip()

            # OpenAI-like / Meta Llama 3.2
            if "choices" in body and isinstance(body["choices"], list) and body["choices"]:
                choice = body["choices"][0]
                if isinstance(choice, dict) and "message" in choice and isinstance(choice["message"], dict):
                    msg = choice["message"]
                    if "content" in msg:
                        content = msg["content"]
                        if isinstance(content, list):
                            texts = []
                            for c in content:
                                if isinstance(c, dict) and c.get("type") == "text" and "text" in c:
                                    texts.append(str(c["text"]))
                            if texts:
                                return "\n".join(texts).strip()
                        # Fallback para string
                        if isinstance(content, str):
                            return content.strip()
                    # Fallbacks
                    if "text" in msg and isinstance(msg["text"], str):
                        return msg["text"].strip()
                if "text" in choice:
                    return str(choice["text"]).strip()
                if "delta" in choice:
                    return json.dumps(choice["delta"], ensure_ascii=False)

            # Titan-like (já ok)
            if "results" in body and isinstance(body["results"], list) and body["results"]:
                first = body["results"][0]
                if isinstance(first, dict) and "outputText" in first:
                    return str(first["outputText"]).strip()

            if "error" in body:
                try:
                    return "__API_ERROR__ " + json.dumps(body["error"], ensure_ascii=False)
                except Exception:
                    return "__API_ERROR__ " + str(body["error"])

            for possible in ("output", "data", "result", "generation", "output_text"):
                if possible in body:
                    return json.dumps(body[possible], ensure_ascii=False)

            return json.dumps(body, ensure_ascii=False)

        return str(body)
    except Exception as e:
        logging.exception("Erro extraindo texto da resposta")
        return f"__PARSE_EXCEPTION__ {e} | raw={repr(resposta_body)}"


# Model input builders


def build_model_input_for_bedrock(prompt: str) -> Dict:
    """
    - Anthropic: schema da Anthropic.
    - Demais (ex.: Meta Llama): estilo 'messages' com blocos.
    """
    if BEDROCK_MODEL_ID.startswith("anthropic."):
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "system": "Analista de perfis de BlueSky",
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ],
            "temperature": 0.2,
            "top_p": 0.9
        }
    else:
        return {
            "messages": [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "Analista de perfis de BlueSky"}]
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ],
            "temperature": 0.2,
            "top_p": 0.9
        }

def model_input_from_doc(doc: Dict) -> Optional[Dict]:
    """
    Constrói o corpo do invoke_model a partir do doc (seleção de posts + prompt).
    Retorna dict com 'recordId' e 'modelInput' ou None.
    """
    source_id = str(doc["_id"])
    tweets_pt = choose_posts(doc.get("posts", []))
    if not tweets_pt:
        return None
    tweets_json = json.dumps(tweets_pt, ensure_ascii=False)
    prompt = build_prompt(tweets_json)
    body = build_model_input_for_bedrock(prompt)
    return {"recordId": source_id, "modelInput": body}


# Persistência do resultado


def _save_report_direct(source_id: str, model_output_any):
    relatorio_raw = extract_text_from_response(model_output_any)
    relatorio_dict = extract_json(relatorio_raw)

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


# Execução ON-DEMAND (invoke_model)


def invoke_once(model_id: str, body: Dict) -> Dict:
    """
    Chama o Bedrock Runtime e retorna o JSON já parseado.
    """
    resp = bedrock_rt.invoke_model(
        modelId=model_id,
        body=json.dumps(body).encode("utf-8"),
        contentType="application/json",
        accept="application/json",
    )
    raw = resp.get("body").read()
    return _normalize_response_body(raw)

def execute_on_demand(records: List[Dict]):
    print(f"[INFO] Executando ON-DEMAND (invoke_model) para {len(records)} registros...")
    ok, fail = 0, 0
    t0 = time.perf_counter()

    for rec in records:
        try:
            parsed = invoke_once(BEDROCK_MODEL_ID, rec["modelInput"])
            _save_report_direct(rec["recordId"], parsed)
            ok += 1
            if ok % 50 == 0:
                print(f"[OK] {ok} processados...")
        except ClientError as e:
            fail += 1
            print(f"[ERRO] invoke_model falhou para {rec['recordId']}: {e}")

    dt = time.perf_counter() - t0
    print(f"[INFO] ON-DEMAND finalizado: {ok} ok / {fail} falhas em {dt:.1f}s")


# Pipeline principal


def processar_bsky_docs(max_docs: Optional[int] = None):
    """
    Busca docs pendentes e processa via invoke_model (on-demand).
    """
    filtro_base = {"significant": True, "report_id": {"$exists": True}, "report_id_bedrock": {"$exists": False}}

    try:
        total = data_coll.count_documents(filtro_base)
        print(f"[INFO] Pendente em `{COL_DATA}`: ~{total} documentos (sem report_id_bedrock)")
    except Exception as e:
        print(f"[WARN] count_documents falhou/foi lento, seguindo sem: {e}")
        total = None

    total_processados = 0

    while True:
        restante = (max_docs - total_processados) if max_docs is not None else None
        if restante is not None and restante <= 0:
            break

        fetch_n = min(DEFAULT_PAGE_SIZE, restante) if restante is not None else DEFAULT_PAGE_SIZE
        docs = list(
            data_coll.find(filtro_base, projection={"posts": 1})
                     .limit(fetch_n)
        )
        if not docs:
            break

        records: List[Dict] = []
        for doc in docs:
            rec = model_input_from_doc(doc)
            if rec:
                records.append(rec)

        if not records:
            # nada selecionado (ex.: posts vazios)
            # marcamos? não, deixamos para outra rotina decidir.
            continue

        print(f"[INFO] Rodando {len(records)} documentos (acumulado: {total_processados + len(records)})")
        execute_on_demand(records)
        total_processados += len(records)

    print(f"[INFO] Finalizado. Processados: {total_processados}{'' if max_docs is None else f' / alvo {max_docs}'}")


# CLI


def main():
    parser = argparse.ArgumentParser(description="Processa contas e gera relatórios via Amazon Bedrock Runtime (Llama 3.2 90B on-demand).")
    parser.add_argument("-n", "--num", type=int, default=None,
                        help="Número MÁXIMO de contas a analisar (default: ilimitado)")
    parser.add_argument("--page-size", type=int, default=None,
                        help="Sobrescreve o page size (docs por iteração)")
    args = parser.parse_args()

    global DEFAULT_PAGE_SIZE
    if args.page_size is not None and args.page_size > 0:
        DEFAULT_PAGE_SIZE = args.page_size
        print(f"[INFO] Page size sobrescrito para {DEFAULT_PAGE_SIZE}")

    if args.num is not None and args.num <= 0:
        print("[INFO] Nada a fazer: --num <= 0")
        return

    print(f"[INFO] Iniciando pipeline ON-DEMAND (Llama 3.2 90B). Limite de contas: {args.num if args.num is not None else 'ilimitado'}")
    processar_bsky_docs(max_docs=args.num)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[INFO] Execução interrompida pelo usuário.")
