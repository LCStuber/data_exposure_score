import os
import sys
import socket
from dotenv import load_dotenv
from atproto import Client
from atproto.exceptions import AtProtocolError
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError

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
auto_client.login(
    os.getenv("BLSKY_USERNAME"),
    os.getenv("BLSKY_PASSWORD")
)

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

        cursor = None
        total = 0

        while True:
            resp = auto_client.app.bsky.graph.get_followers({
                'actor': did,
                'limit': 100,
                'cursor': cursor
            })
            batch = resp['followers']
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
                    # Ignore duplicates or log errors
                    print(f"Warning: could not upsert task for {f['did']}: {e}")

            cursor = getattr(resp, 'cursor', None)
            if not cursor:
                break

        print(f"[{WORKER_ID}] Done: scheduled {total} followers tasks.")
        return total

    except AtProtocolError as e:
        print(f"API error while resolving handle {handle}: {e}")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python populate_tasks.py <bluesky_handle>")
        sys.exit(1)

    target_handle = sys.argv[1]
    count = get_all_followers(target_handle)
    print(f"Scheduled a total of {count} tasks for handle: {target_handle}")