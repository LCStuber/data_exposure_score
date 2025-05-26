import os
import socket
from datetime import datetime
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError, DuplicateKeyError
from concurrent.futures import ThreadPoolExecutor
from atproto import Client
from atproto.exceptions import AtProtocolError
from dotenv import load_dotenv
from pymongo import MongoClient

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
client.login(
    os.getenv("BLSKY_USERNAME"),
    os.getenv("BLSKY_PASSWORD")
)

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
                'locked_at': datetime.utcnow()
            }},
            return_document=ReturnDocument.AFTER
        )

        if not task:
            break

        did    = task['did']
        handle = task['handle']
        print(f"[{WORKER_ID}] Processando @{handle} ({did})…")

        try:
            posts = get_all_posts_of_user(did)
            data_coll.insert_one({
                'did':       did,
                'handle':    handle,
                'posts':     posts,
                'fetched_at': datetime.utcnow()
            })
            tasks_coll.update_one(
                {'_id': task['_id']},
                {'$set': {
                    'status':       'done',
                    'processed_at': datetime.utcnow()
                }}
            )
            print(f"[{WORKER_ID}] Concluído: {len(posts)} posts de @{handle}.")

        except Exception as e:
            print(f"[{WORKER_ID}] Erro em @{handle}: {e}")
            tasks_coll.update_one(
                {'_id': task['_id']},
                {'$set': {
                    'status':       'failed',
                    'error':        str(e),
                    'processed_at': datetime.utcnow()
                }}
            )

if __name__ == "__main__":
    num_threads = os.cpu_count() or 4
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(lambda _: process_tasks(), range(num_threads))