import os
import sys
import socket
from dotenv import load_dotenv
from atproto import Client
from atproto_client.exceptions import RequestException, AtProtocolError
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError
import time

# Load environment variables
load_dotenv()

# MongoDB configuration
USER = os.getenv("MONGO_USER")
PASS = os.getenv("MONGO_PASS")
HOST = os.getenv("MONGO_HOST")
PORT = os.getenv("MONGO_PORT")
AUTH_DB = os.getenv("MONGO_AUTH_DB")
DB_NAME = os.getenv("MONGO_DB")
TASKS_COLLECTION = os.getenv("MONGO_COLLECTION_TASKS", "tasks")

# Build MongoDB URI and client
uri = f"mongodb://{USER}:{PASS}@{HOST}:{PORT}/?authSource={AUTH_DB}"
client_db = MongoClient(uri)
db = client_db[DB_NAME]
tasks_coll = db[TASKS_COLLECTION]

# ATProto client setup
auto_client = Client()

# Login ATProto
max_retries = 5
retries = 0

while True:
    try:
        auto_client.login(
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

# Worker identifier for logging (hostname)
WORKER_ID = socket.gethostname()


def get_all_followers(handle: str) -> int:
    """
    Fetches all followers of the specified handle and upserts entries into `tasks_coll`.
    Returns the number of followers scheduled.
    """
    try:
        profile = auto_client.com.atproto.identity.resolve_handle({'handle': handle})
        did = profile['did']
    except AtProtocolError as e:
        print(f"API error while resolving handle {handle}: {e}")
        return 0

    cursor = None
    total = 0

    while True:
        try:
            resp = auto_client.app.bsky.graph.get_followers({
                'actor': did,
                'limit': 100,
                'cursor': cursor
            })

        except RequestException as e:
            resp_obj = getattr(e, 'response', None)
            status   = resp_obj.status_code if resp_obj else None
            headers  = resp_obj.headers     if resp_obj else {}

            # Rate limit handling
            if status == 429 or 'RateLimitExceeded' in str(e):
                reset_ts = int(headers.get('ratelimit-reset', 0))
                wait = max(reset_ts - time.time(), 0) + 1
                print(f"[{WORKER_ID}] Rate limit atingido para {did}. Aguardando {wait:.0f}s…")
                time.sleep(wait)
                continue
            else:
                print(f"[{WORKER_ID}] Erro crítico ao buscar followers de {did}: {e}")
                return total

        batch = resp['followers'] or []
        total += len(batch)
        print(f"[{WORKER_ID}] Collected {total} followers so far...")

        for f in batch:
            try:
                tasks_coll.update_one(
                    {'did': f['did']},
                    {'$setOnInsert': {
                        'did':       f['did'],
                        'handle':    f['handle'],
                        'status':    'pending',
                        'locked_by': None
                    }},
                    upsert=True
                )
            except (DuplicateKeyError, PyMongoError) as e:
                print(f"Warning: could not upsert task for {f['did']}: {e}")

        cursor = resp.cursor
        if not cursor:
            break

    print(f"[{WORKER_ID}] Done: scheduled {total} followers tasks.")
    return total


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python populate_tasks.py <bluesky_handle>")
        sys.exit(1)

    target_handle = sys.argv[1]
    count = get_all_followers(target_handle)
    print(f"Scheduled a total of {count} tasks for handle: {target_handle}")