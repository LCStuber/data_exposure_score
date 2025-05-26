import os
import socket
from datetime import datetime, timezone
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError, DuplicateKeyError
from concurrent.futures import ThreadPoolExecutor
from atproto import Client
from atproto_client.exceptions import RequestException
from dotenv import load_dotenv
from pymongo import MongoClient
import time
import sys

load_dotenv()

# MongoDB setup
USER       = os.getenv("MONGO_USER")
PASS       = os.getenv("MONGO_PASS")
HOST       = os.getenv("MONGO_HOST")
PORT       = os.getenv("MONGO_PORT")
AUTH_DB    = os.getenv("MONGO_AUTH_DB")
DB_NAME    = os.getenv("MONGO_DB")

uri = f"mongodb://{USER}:{PASS}@{HOST}:{PORT}/?authSource={AUTH_DB}"
clientDB   = MongoClient(uri)
db         = clientDB[DB_NAME]

# usa o hostname como WORKER_ID por padrão
WORKER_ID  = os.getenv("WORKER_ID", socket.gethostname())

# Collections
tasks_coll = db[os.getenv("MONGO_COLLECTION_TASKS")]
data_coll  = db[os.getenv("MONGO_COLLECTION_DATA")]

# ATProto client
client = Client()

# Login ATProto
max_retries = 5
retries = 0

while True:
    try:
        client.login(
            os.getenv("BLSKY_USERNAME"),
            os.getenv("BLSKY_PASSWORD")
        )
        print("Login bem-sucedido")
        break

    except RequestException as e:
        resp    = getattr(e, 'response', None)
        status  = resp.status_code if resp else None
        headers = resp.headers     if resp else {}

        # Se for rate-limit, espera até o reset
        if status == 429 or 'RateLimitExceeded' in str(e):
            reset_ts = int(headers.get('ratelimit-reset', 0))
            wait = max(reset_ts - time.time(), 0) + 1
            print(f"Rate limit atingido no login. Aguardando {wait:.0f}s…")
            time.sleep(wait)
            retries += 1
            if retries >= max_retries:
                raise RuntimeError("Número máximo de tentativas de login excedido.")
            continue

        # Qualquer outro RequestException
        print(f"Erro no login (RequestException): {e}")
        raise

    except Exception as e:
        # Erros inesperados
        print(f"Erro crítico no login: {e}")
        raise

def get_all_posts_of_user(did: str):
    all_posts = []
    cursor = None

    while True:
        try:
            response = client.app.bsky.feed.get_author_feed({
                'actor': did,
                'limit': 100,
                'cursor': cursor
            })

            feed = response.feed or []
            for post in feed:
                all_posts.append({
                    'text':       post.post.record.text,
                    'created_at': post.post.record.created_at
                })

            cursor = response.cursor
            if not cursor:
                break

        except RequestException as e:
            resp    = getattr(e, 'response', None)
            status  = resp.status_code if resp else None
            headers = resp.headers     if resp else {}

            if status == 429 or 'RateLimitExceeded' in str(e):
                reset_ts = int(headers.get('ratelimit-reset', 0))
                wait = max(reset_ts - time.time(), 0) + 1
                print(f"Rate limit atingido para {did}. Aguardando {wait:.0f}s…")
                time.sleep(wait)
                continue
            else:
                print(f"Erro crítico ao buscar posts de {did}: {e}")
                break

        except Exception as e:
            print(f"Erro ao buscar posts de {did}: {e}")
            break

    return all_posts

def process_tasks():
    while True:
        task = tasks_coll.find_one_and_update(
            {'status': 'pending'},
            {'$set': {
                'status':    'processing',
                'locked_by': WORKER_ID,
                'locked_at': datetime.now(timezone.utc)
            }},
            return_document=ReturnDocument.AFTER
        )

        if not task:
            break

        did    = task['did']
        print(f"[{WORKER_ID}] Processando {did} …")

        try:
            posts = get_all_posts_of_user(did)
            data_coll.insert_one({
                'posts':     posts,
                'fetched_at': datetime.now(timezone.utc)
            })
            tasks_coll.update_one(
                {'_id': task['_id']},
                {'$set': {
                    'status':       'done',
                    'processed_at': datetime.now(timezone.utc)
                }}
            )
            print(f"[{WORKER_ID}] Concluído: {len(posts)} posts de {did}.")

        except Exception as e:
            print(f"[{WORKER_ID}] Erro em {did}: {e}")
            tasks_coll.update_one(
                {'_id': task['_id']},
                {'$set': {
                    'status':       'failed',
                    'error':        str(e),
                    'processed_at': datetime.now(timezone.utc)
                }}
            )
            sys.exit(1)

if __name__ == "__main__":
    num_threads = os.cpu_count() or 4
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(lambda _: process_tasks(), range(num_threads))