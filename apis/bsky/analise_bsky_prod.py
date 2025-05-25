from atproto import Client
from atproto.exceptions import AtProtocolError
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

USER       = os.getenv("MONGO_USER")
PASS       = os.getenv("MONGO_PASS")
HOST       = os.getenv("MONGO_HOST")
PORT       = os.getenv("MONGO_PORT")
AUTH_DB    = os.getenv("MONGO_AUTH_DB")

DB_NAME    = os.getenv("MONGO_DB")
COLLECTION = os.getenv("MONGO_COLLECTION")

client = Client()
client.login(
    os.getenv("BLSKY_USERNAME"),
    os.getenv("BLSKY_PASSWORD")
)

def get_all_followers(handle: str):
    try:
        profile = client.com.atproto.identity.resolve_handle({'handle': handle})
        did = profile['did']

        followers = []
        cursor = None

        while True:
            response = client.app.bsky.graph.get_followers({
                'actor': did,
                'limit': 100,
                'cursor': cursor
            })

            followers_batch = response['followers']
            followers.extend(followers_batch)

            # Opcional: log de progresso
            print(f"Coletados {len(followers)} seguidores até agora...")

            # Checa se há um cursor para continuar
            cursor = response.cursor
            if not cursor:
                break

        return followers

    except AtProtocolError as e:
        print(f"Erro na API: {e}")
        return []
    
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

            feed = response.feed

            if not feed:
                break

            for post in feed:
                post_data = {
                    'text': post.post.record.text,
                    'created_at': post.post.record.created_at
                }
                all_posts.append(post_data)

            cursor = response.cursor
            if not cursor:
                break

        except Exception as e:
            print(f"Erro ao buscar posts de {did}: {e}")
            break

    return all_posts

uri = f"mongodb://{USER}:{PASS}@{HOST}:{PORT}/?authSource={AUTH_DB}"
clientDB = MongoClient(uri)

db = clientDB[DB_NAME]
collection = db[COLLECTION]

def save_incrementally(data):
    """
    Insere o dicionário `data` na coleção configurada em .env
    """
    try:
        result = collection.insert_one(data)
        print(f"Dados salvos com sucesso. _id gerado: {result.inserted_id}")
    except PyMongoError as e:
        print(f"Erro ao salvar no MongoDB: {e}")


handle = 'duolingobrasil.com.br'
followers = get_all_followers(handle)
print(f'Total de seguidores: {len(followers)}')

for follower in followers:
    follower_did = follower['did']
    follower_handle = follower['handle']

    print(f"Buscando posts de @{follower_handle} ({follower_did})...")

    posts = get_all_posts_of_user(follower_did)

    user_data = {
        'posts': posts
    }

    save_incrementally(user_data)

    print(f"Coletados {len(posts)} posts de @{follower_handle}.\n")