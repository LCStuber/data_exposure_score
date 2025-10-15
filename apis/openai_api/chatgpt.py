import os
import sys
import json
import time
import tempfile
import re
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Optional
from bson import ObjectId

from openai import OpenAI
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
COL_REPORT = os.getenv("MONGO_COLLECTION_REPORTS")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

TLS_CA_FILE = os.getenv("MONGO_TLS_CA_FILE", "rds-combined-ca-bundle.pem")

DEFAULT_BATCH_SIZE = int(os.getenv("BATCH_SIZE", 500))  # linhas por arquivo .jsonl para Batch API
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1")

if not all([USER, PASS, HOST, PORT, AUTH_DB, DB_NAME, COL_DATA, COL_REPORT, OPENAI_KEY]):
    raise RuntimeError("Verifique se todas as variáveis de ambiente Mongo e OPENAI_API_KEY estão configuradas no .env")

# MongoDB client
uri = (
    f"mongodb://{HOST}:{PORT}"
    f"/?tls=true&tlsCAFile={TLS_CA_FILE}&replicaSet=rs0&readPreference=secondaryPreferred"
    f"&retryWrites=false&authSource={AUTH_DB}"
)
clientDB = MongoClient(uri,
                       username=USER,
                       password=PASS
                       )
db = clientDB[DB_NAME]
data_coll = db[COL_DATA]
reports_coll = db[COL_REPORT]

def ensure_indexes():
    try:
        reports_coll.create_index("source_id", unique=True)
    except Exception as e:
        print(f"[WARN] create_index(reports.source_id) ignorado: {e}")
    try:
        data_coll.create_index([("significant", 1), ("report_id", 1)])
    except Exception as e:
        print(f"[WARN] create_index(data.significant, report_id) ignorado: {e}")

ensure_indexes()


# OpenAI client


openai_client = OpenAI(api_key=OPENAI_KEY)

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

# Helpers de prompt, seleção e parsing

def build_prompt(tweets_json: str) -> str:
    return (
        "Você é um analista de perfis do Twitter/BlueSky.\n"
        "Analise os tweets e RETORNE ESTRITAMENTE um JSON válido, sem markdown e sem comentários.\n"
        "Formato:\n"
        "{\n"
        '  "InformacoesIniciais": { <TODOS os CAMPOS abaixo com valores "VERDADEIRO" ou "FALSO"> },\n'
        '  "InformacoesAdicionais": { "Idade": <string ou null>, "Genero": <string ou null>, "DataUltimoTweet": <ISO8601 ou null> }\n'
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


# Batch line builder


def doc_to_batch_line(doc: Dict) -> Optional[Dict]:
    """Transforma um documento Mongo em uma linha JSONL para o Batch API"""
    source_id = str(doc["_id"])
    tweets_pt = choose_posts(doc.get("posts", []))
    if not tweets_pt:
        return None

    tweets_json = json.dumps(tweets_pt, ensure_ascii=False)
    prompt = build_prompt(tweets_json)

    body = {
        "model": MODEL_NAME,
        "input": [
            {"role": "system", "content": "Analista de perfis de BlueSky"},
            {"role": "user", "content": prompt}
        ],
        "store": False,
    }

    return {
        "custom_id": source_id,
        "method": "POST",
        "url": "/v1/responses",
        "body": body,
    }


# Arquivo JSONL para Batch


def write_jsonl(lines: List[Dict]) -> str:
    """Escreve as linhas da batch em um arquivo temporário .jsonl e retorna o caminho"""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl", mode="w", encoding="utf-8")
    for line in lines:
        tmp.write(json.dumps(line, ensure_ascii=False) + "\n")
    tmp.close()
    return tmp.name


# Espera pelo Batch


def wait_batch(batch_id: str, poll_seconds: int = 60):
    """Aguarda até que o batch mude para estado 'completed' ou 'failed'/'cancelled'"""
    print(f"[INFO] Aguardando conclusão do batch {batch_id}...")
    while True:
        batch = openai_client.batches.retrieve(batch_id)
        status = getattr(batch, "status", None)
        counts = getattr(batch, "request_counts", None)
        if status in {"completed", "failed", "cancelled", "expired"}:
            return batch
        if counts:
            print(f"    status: {status} | concluído: {counts.completed} / {counts.total}")
        else:
            print(f"    status: {status}")
        time.sleep(poll_seconds)

def _iter_lines_from_file(file_id: str):
    """Itera linhas do arquivo de saída sem carregar tudo na memória."""
    resp = openai_client.files.content(file_id)
    if hasattr(resp, "iter_lines"):
        for b in resp.iter_lines():
            if b:
                yield b.decode("utf-8")
    else:
        text = resp.text
        for line in text.splitlines():
            if line:
                yield line


# Processamento de resultados


def processar_resultados(batch):
    """Baixa o arquivo de saída do batch e processa cada linha para Mongo"""
    output_file_id = getattr(batch, "output_file_id", None)
    error_file_id = getattr(batch, "error_file_id", None)

    if not output_file_id:
        print(f"[ERRO] Batch {batch.id} não possui output_file_id. Status: {batch.status}")
        return

    processed = 0
    for line in _iter_lines_from_file(output_file_id):
        registro = json.loads(line)
        source_id = registro["custom_id"]

        resposta_body = registro["response"]["body"]
        relatorio_raw = resposta_body["choices"][0]["message"]["content"].strip()
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
                {"_id": ObjectId(source_id), "report_id": {"$exists": False}},
                {"$set": {"report_id": inserted_id}}
            )

            processed += 1
            if processed % 50 == 0:
                print(f"[OK] Processados {processed} reports...")
        except Exception as e:
            print(f"[ERRO] Falha ao salvar relatório/atualizar doc {source_id}: {e}")

    if error_file_id:
        try:
            err_resp = openai_client.files.content(error_file_id)
            err_path = f"errors_{batch.id}.jsonl"
            with open(err_path, "wb") as f:
                content = getattr(err_resp, "content", None)
                if content is not None:
                    f.write(content)
                else:
                    f.write(err_resp.text.encode("utf-8"))
            print(f"[AVISO] Existem erros no batch. Arquivo salvo em: {err_path}")
        except Exception as e:
            print(f"[WARN] Não foi possível baixar/salvar o arquivo de erros: {e}")


# Pipeline principal


def processar_bsky_docs(max_docs: Optional[int] = None):
    """
    Processa documentos da coleção de dados e cria batches.
    :param max_docs: número máximo de contas a analisar; None = ilimitado
    """
    filtro = {"significant": True, "report_id": {"$exists": False}}

    try:
        total = data_coll.count_documents(filtro)
        print(f"[INFO] Pendente em `{COL_DATA}`: {total} documentos (sem report_id)")
    except Exception as e:
        print(f"[WARN] count_documents falhou/foi lento, seguindo sem: {e}")

    cursor = data_coll.find(filtro, projection={"posts": 1})

    batch_lines: List[Dict] = []
    since_batch = time.perf_counter()
    total_enfileirados = 0

    for doc in cursor:
        if max_docs is not None and total_enfileirados >= max_docs:
            break

        line = doc_to_batch_line(doc)
        if not line:
            continue
        batch_lines.append(line)
        total_enfileirados += 1

        # fecha batch quando atingir o DEFAULT_BATCH_SIZE
        if len(batch_lines) >= DEFAULT_BATCH_SIZE:
            elapsed = time.perf_counter() - since_batch
            print(f"[INFO] Fechando batch de {len(batch_lines)} reqs (acumuladas: {total_enfileirados}) | +{elapsed:.1f}s")
            execute_batch(batch_lines)
            batch_lines.clear()
            since_batch = time.perf_counter()

    # Processa o restante
    if batch_lines:
        elapsed = time.perf_counter() - since_batch
        print(f"[INFO] Fechando último batch de {len(batch_lines)} reqs (total enfileirado: {total_enfileirados}) | +{elapsed:.1f}s")
        execute_batch(batch_lines)

    print(f"[INFO] Finalizado. Contas enfileiradas para análise: {total_enfileirados}{'' if max_docs is None else f' / alvo {max_docs}'}")

# Execução do batch

def execute_batch(lines: List[Dict]):
    """Executa um batch dado uma lista de linhas JSONL"""
    print(f"[INFO] Criando batch com {len(lines)} requisições...")
    jsonl_path = write_jsonl(lines)

    with open(jsonl_path, "rb") as fh:
        file_obj = openai_client.files.create(file=fh, purpose="batch")
    print(f"    Arquivo enviado: {file_obj.id}")

    batch_obj = openai_client.batches.create(
        input_file_id=file_obj.id,
        endpoint="/v1/responses",
        completion_window="24h",
        metadata={"origin": "twitter-bsky-script"}
    )
    print(f"    Batch iniciado: {batch_obj.id} | status: {batch_obj.status}")

    batch_final = wait_batch(batch_obj.id, poll_seconds=60)

    if batch_final.status == "completed":
        processar_resultados(batch_final)
    else:
        print(f"[ERRO] Batch {batch_final.id} terminou com status {batch_final.status}")


# Main (CLI)


def main():
    parser = argparse.ArgumentParser(description="Processa contas e gera relatórios via OpenAI Batch.")
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

    print(f"[INFO] Iniciando pipeline. Limite de contas: {args.num if args.num is not None else 'ilimitado'}")
    processar_bsky_docs(max_docs=args.num)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[INFO] Execução interrompida pelo usuário.")
