#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para varrer todos os documentos da collection `MONGO_COLLECTION_DATA` e, em cada `post`, adicionar
campo "lang" com o idioma detectado de `text`.

Os parâmetros de conexão (usuário, senha, host, porta, authDB, dbName e collection) são carregados de um
arquivo `.env` (via python-dotenv). 

Você ainda pode passar, opcionalmente, como argumentos:
  --batch-size   (tamanho do lote de documentos para cada iteração)
  --num-workers  (quantos processos filhos usar para detecção de idioma)
  --num-shards   (quantos shards/máquinas no total)
  --shard-index  (índice deste shard, de 0 a num-shards-1)

Se não passar `--num-shards` nem `--shard-index` na CLI, tentaremos usar as variáveis de ambiente
NUM_SHARDS e SHARD_INDEX (ou cair nos padrões 1 e 0, respectivamente).
"""

import os
import argparse
import hashlib
import logging
import multiprocessing as mp
import sys
import traceback

from itertools import islice
from functools import partial

from pymongo import MongoClient
from bson.objectid import ObjectId
from langdetect import DetectorFactory, detect, LangDetectException
from dotenv import load_dotenv
from tqdm import tqdm

# --------------------------------
#  CARREGA VARIÁVEIS DO .env
# --------------------------------
load_dotenv()  # Carrega as variáveis definidas em .env para o os.environ

# Variáveis de conexão ao Mongo (obrigatórias)
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_AUTH_DB = os.getenv("MONGO_AUTH_DB")

# Banco e coleção onde estão os dados
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION_DATA = os.getenv("MONGO_COLLECTION_DATA")

# (Opcional) coleção de tasks, caso queira usar depois
MONGO_COLLECTION_TASKS = os.getenv("MONGO_COLLECTION_TASKS")

# Shardização (caso queira dividir o processamento em N máquinas via ENV)
ENV_NUM_SHARDS = os.getenv("NUM_SHARDS")
ENV_SHARD_INDEX = os.getenv("SHARD_INDEX")

# Validações mínimas das variáveis de ambiente
if not all([MONGO_USER, MONGO_PASS, MONGO_AUTH_DB, MONGO_DB, MONGO_COLLECTION_DATA]):
    print("❌ ERRO: Falta configurar alguma variável no .env. Certifique-se de ter:")
    print("   MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_AUTH_DB, MONGO_DB, MONGO_COLLECTION_DATA")
    sys.exit(1)

# --------------------------------
#  CONFIGURAÇÕES GLOBAIS DE LOGGER
# --------------------------------
DetectorFactory.seed = 0  # para resultados reproduzíveis do langdetect

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# --------------------------------
#  FUNÇÕES AUXILIARES
# --------------------------------

def build_mongo_uri():
    """
    Monta a string de conexão (URI) a partir das variáveis de ambiente.
    Exemplo resultante: 
      mongodb://bsky_app:minhaSenha@localhost:27017/des
    """
    user = MONGO_USER
    pwd = MONGO_PASS
    host = MONGO_HOST
    port = MONGO_PORT
    auth_db = MONGO_AUTH_DB

    # Se a senha (MONGO_PASS) contiver caracteres especiais, escaponar não é estritamente necessário 
    # nesta string (o driver do pymongo já trata), mas cuidado com espaços ou caracteres não-ASCII.
    uri = f"mongodb://{user}:{pwd}@{host}:{port}/{auth_db}"
    return uri


def compute_shard_for_id(oid: ObjectId, num_shards: int) -> int:
    """
    Recebe um ObjectId e calcula, via hash SHA1 do seu str(), a qual shard (0..num_shards-1) ele pertence.
    Assim dá para dividir o mesmo conjunto de documentos entre N máquinas diferentes de forma pseudo-uniforme.
    """
    oid_str = str(oid)
    digest = hashlib.sha1(oid_str.encode("utf-8")).digest()
    primeiro_byte = digest[0]
    return primeiro_byte % num_shards


def detect_lang_for_post(post_dict: dict) -> str:
    """
    Dado um dicionário de post (com chave 'text'), detecta o idioma usando langdetect.
    Se o texto for muito curto ou der erro, retorna 'und' (indefinido).
    """
    texto = post_dict.get("text", "") or ""
    texto = texto.strip()
    if len(texto) < 3:
        return "und"
    try:
        return detect(texto)
    except LangDetectException:
        return "und"
    except Exception:
        return "und"


def process_document(doc: dict) -> tuple:
    """
    Função executada pelos workers (multiprocess). Recebe um documento (com '_id' e 'posts'),
    adiciona 'lang' a cada post e retorna (doc_id, lista_de_posts_atualizada).

    Se der erro, retorna (doc_id, None). O processo pai decide o retry ou pular.
    """
    doc_id = doc["_id"]
    posts = doc.get("posts", [])
    updated_posts = []

    try:
        for post in posts:
            # Clona campos originais do post para não alterar diretamente o doc que veio do cursor
            novo_post = dict(post)
            lang = detect_lang_for_post(novo_post)
            novo_post["lang"] = lang
            updated_posts.append(novo_post)
        return (doc_id, updated_posts)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"[Worker] Erro ao processar doc_id={doc_id}: {e}\n{tb}")
        return (doc_id, None)


def chunked_cursor(cursor, size):
    """
    Recebe um cursor do PyMongo e produz listas (batches) de até 'size' elementos.
    Exemplo: se size=1000, a primeira chamada devolve uma lista com os 1.000 primeiros docs;
    depois mais 1.000, etc., até esgotar.
    """
    while True:
        batch = list(islice(cursor, size))
        if not batch:
            break
        yield batch


# --------------------------------
#  FUNÇÃO PRINCIPAL
# --------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Detecta idioma para cada post na coleção especificada pelo .env (MONGO_COLLECTION_DATA)."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Número de documentos por lote (batch) para cada iteração (padrão: 1000)."
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=os.cpu_count() or 4,
        help="Número de processos simultâneos para detecção de idioma (padrão: 4)."
    )
    parser.add_argument(
        "--num-shards",
        type=int,
        default=None,
        help="Quantidade total de shards (máquinas). Se não informado, busca ENV_NUM_SHARDS ou assume 1."
    )
    parser.add_argument(
        "--shard-index",
        type=int,
        default=None,
        help="Índice deste shard (0 a num-shards-1). Se não informado, busca ENV_SHARD_INDEX ou assume 0."
    )

    args = parser.parse_args()

    # 1) Determina num_shards e shard_index, levando em conta CLI > ENV > default
    try:
        if args.num_shards is not None:
            num_shards = args.num_shards
        else:
            num_shards = int(ENV_NUM_SHARDS) if ENV_NUM_SHARDS is not None else 1
    except ValueError:
        logger.error("🛑 Valor inválido em NUM_SHARDS no .env. Deve ser inteiro.")
        sys.exit(1)

    try:
        if args.shard_index is not None:
            shard_index = args.shard_index
        else:
            shard_index = int(ENV_SHARD_INDEX) if ENV_SHARD_INDEX is not None else 0
    except ValueError:
        logger.error("🛑 Valor inválido em SHARD_INDEX no .env. Deve ser inteiro.")
        sys.exit(1)

    if shard_index < 0 or shard_index >= num_shards:
        logger.error("🛑 Erro: shard_index deve estar entre 0 e num_shards-1.")
        sys.exit(1)

    batch_size = args.batch_size
    num_workers = args.num_workers

    logger.info(f"Parâmetros de shardização: num_shards={num_shards}, shard_index={shard_index}")
    logger.info(f"Batch size={batch_size}, Num workers={num_workers}")

    # 2) Monta URI e abre conexão MongoDB
    mongo_uri = build_mongo_uri()
    logger.info(f"Conectando ao MongoDB em {MONGO_HOST}:{MONGO_PORT}, authDB={MONGO_AUTH_DB} ...")
    try:
        client = MongoClient(mongo_uri)
    except Exception as e:
        logger.error(f"Falha ao conectar ao MongoDB: {e}")
        sys.exit(1)

    db = client[MONGO_DB]
    coll = db[MONGO_COLLECTION_DATA]

    # 3) Contagem aproximada (estimated) de documentos
    try:
        total_docs = coll.estimated_document_count()
    except Exception as e:
        logger.warning(f"Não consegui estimar o número de documentos: {e}")
        total_docs = None

    if total_docs is not None:
        logger.info(f"Total estimado de documentos na coleção: {total_docs}")
    else:
        logger.info("Não foi possível obter contagem estimada de documentos.")

    # 4) Cria pool de workers
    logger.info(f"Criando pool de {num_workers} processos (multiprocessing).")
    pool = mp.Pool(processes=num_workers)

    # 5) Monta cursor — apenas _id e posts, para economizar banda/CPU
    try:
        cursor = coll.find({"posts.lang": {"$exists": False}}, {"posts": 1})
    except Exception as e:
        logger.error(f"Falha ao criar cursor: {e}")
        client.close()
        sys.exit(1)

    processed = 0
    batch_number = 0

    # 6) Itera em batches de tamanho batch_size
    for batch in chunked_cursor(cursor, batch_size):
        batch_number += 1
        logger.info(f"Iniciando batch #{batch_number} (tamanho lido: {len(batch)})")

        # 6.1) Filtra localmente somente documentos que pertencem a este shard
        if num_shards > 1:
            filtered = []
            for doc in batch:
                if compute_shard_for_id(doc["_id"], num_shards) == shard_index:
                    filtered.append(doc)
            if not filtered:
                # Nenhum documento deste lote pertence a este shard
                continue
            to_process = filtered
        else:
            to_process = batch

        # 6.2) Mapeia os documentos para o pool de workers (detecta idioma)
        try:
            results = pool.map(process_document, to_process)
        except Exception as e:
            logger.error(f"Erro no pool.map: {e}")
            break

        # 6.3) Processa resultados e executa update no MongoDB (somente no processo principal)
        for doc_id, updated_posts in results:
            if updated_posts is None:
                logger.warning(f"Pulando update do doc_id={doc_id} (detect_lang falhou).")
                continue

            filtro = {"_id": doc_id}
            update = {"$set": {"posts": updated_posts}}
            try:
                coll.update_one(filtro, update)
                processed += 1
            except Exception as e:
                logger.error(f"Falha ao atualizar doc_id={doc_id}: {e}")

        logger.info(f"Batch #{batch_number} concluído. Atualizados: {len(results)} docs neste lote.")

    # 7) Finaliza pool e conexão
    pool.close()
    pool.join()
    client.close()

    logger.info(f"✨ Processamento finalizado. Total aproximado de documentos atualizados: {processed}")


if __name__ == "__main__":
    main()
