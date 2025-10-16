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


# Batch line builder


def _normalize_response_body(raw):
    """
    Garante que raw seja um dict (quando possível). Se não for JSON, devolve como string.
    """
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", errors="replace")
    if isinstance(raw, str):
        raw_str = raw.strip()
        # tenta desserializar uma vez (pode ser string com JSON dentro)
        try:
            parsed = json.loads(raw_str)
            # Se devolveu uma string (JSON serializado dentro de uma string), tenta novamente
            if isinstance(parsed, str):
                try:
                    parsed2 = json.loads(parsed)
                    return parsed2
                except Exception:
                    return parsed  # é só uma string normal
            return parsed
        except Exception:
            return raw_str
    return raw  # já é dict/list ou outro objeto

def extract_text_from_response(resposta_body):
    """
    Retorna o texto útil do objeto de resposta (ou uma string de erro/fallback).
    """
    try:
        body = _normalize_response_body(resposta_body)
        # Se for string já normalizado, devolve-o
        if isinstance(body, str):
            return body

        # 1) padrão OpenAI Chat/Completions
        if isinstance(body, dict):
            # se houver choices
            if "choices" in body and isinstance(body["choices"], (list, tuple)) and len(body["choices"]) > 0:
                choice = body["choices"][0]
                # Chat completions estilo: {"message": {"content": "..."}}
                if isinstance(choice, dict):
                    if "message" in choice and isinstance(choice["message"], dict) and "content" in choice["message"]:
                        return str(choice["message"]["content"]).strip()
                    # Completions estilo antigo: {"text": "..."}
                    if "text" in choice:
                        return str(choice["text"]).strip()
                    # Delta streaming content (pode precisar de tratamento)
                    if "delta" in choice:
                        return json.dumps(choice["delta"], ensure_ascii=False)
            # 2) se houver campo de erro
            if "error" in body:
                try:
                    return "__API_ERROR__ " + json.dumps(body["error"], ensure_ascii=False)
                except Exception:
                    return "__API_ERROR__ " + str(body["error"])
            # 3) outros campos comuns
            for possible in ("output", "results", "result", "data"):
                if possible in body:
                    return json.dumps(body[possible], ensure_ascii=False)
            # 4) fallback: devolve o corpo inteiro serializado
            return json.dumps(body, ensure_ascii=False)
        # Se chegamos aqui, devolve string do objeto
        return str(body)
    except Exception as e:
        logging.exception("Erro extraindo texto da resposta")
        return f"__PARSE_EXCEPTION__ {e} | raw={repr(resposta_body)}"



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
        "messages": [
            {"role": "system", "content": "Analista de perfis de BlueSky"},
            {"role": "user", "content": prompt}
        ],
        "store": False,
    }

    return {
        "custom_id": source_id,
        "method": "POST",
        "url": "/v1/chat/completions",
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
    """Itera linhas do arquivo de saída tratando bytes/str e JSONs 'entre aspas'."""
    resp = openai_client.files.content(file_id)
    if hasattr(resp, "iter_lines"):
        for b in resp.iter_lines():
            if not b:
                continue
            # 1) garantir que temos str
            if isinstance(b, (bytes, bytearray)):
                line = b.decode("utf-8")
            else:
                line = b
            line = line.strip()
            if not line:
                continue

            # 2) tentar descarregar JSON — pode ser: {"a":1}  OU  "\"{...}\""  (string com JSON dentro)
            try:
                parsed_once = json.loads(line)
            except Exception:
                # não é JSON — devolve a linha original
                yield line
                continue

            # Se parsed_once for string -> possivelmente contém o JSON "real" (escapado)
            if isinstance(parsed_once, str):
                try:
                    parsed_twice = json.loads(parsed_once)
                    # se virou dict/list, re-serializamos para manter saída como string JSON
                    if isinstance(parsed_twice, (dict, list)):
                        yield json.dumps(parsed_twice, ensure_ascii=False)
                    else:
                        # primitivos -> devolve como string
                        yield str(parsed_twice)
                except Exception:
                    # parsed_once era só uma string comum: devolve-a
                    yield parsed_once
            elif isinstance(parsed_once, (dict, list)):
                # já é objeto JSON: re-serializa para string (compatibilidade)
                yield json.dumps(parsed_once, ensure_ascii=False)
            else:
                # número, bool etc. -> devolve como string
                yield str(parsed_once)
    else:
        # fallback: usar .text ou .content
        text = getattr(resp, "text", None)
        if text is None:
            content = getattr(resp, "content", None)
            if content is None:
                return
            text = content.decode("utf-8") if isinstance(content, (bytes, bytearray)) else str(content)
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                parsed_once = json.loads(line)
                if isinstance(parsed_once, str):
                    try:
                        parsed_twice = json.loads(parsed_once)
                        if isinstance(parsed_twice, (dict, list)):
                            yield json.dumps(parsed_twice, ensure_ascii=False)
                        else:
                            yield str(parsed_twice)
                    except Exception:
                        yield parsed_once
                elif isinstance(parsed_once, (dict, list)):
                    yield json.dumps(parsed_once, ensure_ascii=False)
                else:
                    yield str(parsed_once)
            except Exception:
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
        relatorio_raw = extract_text_from_response(resposta_body)
        # se o resultado indicar erro da API, trate / logue / re-tente conforme sua lógica:
        if isinstance(relatorio_raw, str) and relatorio_raw.startswith("__API_ERROR__"):
            logging.error("API retornou erro: %s", relatorio_raw)        
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
    Processa documentos da coleção de dados criando batches sem manter cursors abertos
    durante a espera pelos resultados (evita CursorNotFound no DocumentDB).
    """
    filtro_base = {"significant": True, "report_id": {"$exists": False}}

    try:
        total = data_coll.count_documents(filtro_base)
        print(f"[INFO] Pendente em `{COL_DATA}`: {total} documentos (sem report_id)")
    except Exception as e:
        print(f"[WARN] count_documents falhou/foi lento, seguindo sem: {e}")

    total_enfileirados = 0

    while True:
        # Respeita --num, se fornecido
        restante = (max_docs - total_enfileirados) if max_docs is not None else None
        if restante is not None and restante <= 0:
            break

        # Quanto buscar neste ciclo
        fetch_n = min(DEFAULT_BATCH_SIZE, restante) if restante is not None else DEFAULT_BATCH_SIZE

        # >>> MATERIALIZA EM LISTA (fecha o cursor logo em seguida) <<<
        docs = list(
            data_coll.find(filtro_base, projection={"posts": 1})
                     .limit(fetch_n)
        )

        if not docs:
            break  # nada mais a processar

        batch_lines: List[Dict] = []
        since_batch = time.perf_counter()

        for doc in docs:
            line = doc_to_batch_line(doc)
            if line:
                batch_lines.append(line)

        if not batch_lines:
            # Pode acontecer caso vários docs não tenham posts em pt, etc.
            continue

        elapsed = time.perf_counter() - since_batch
        print(f"[INFO] Fechando batch de {len(batch_lines)} reqs (acumuladas: {total_enfileirados + len(batch_lines)}) | +{elapsed:.1f}s")

        execute_batch(batch_lines)  # aqui você espera o batch terminar, sem cursor aberto

        total_enfileirados += len(batch_lines)

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
        endpoint="/v1/chat/completions",
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