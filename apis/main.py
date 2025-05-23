import os
import sys
import pandas as pd
from dotenv import load_dotenv
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apis.openai_api import chatgpt as api_connection


load_dotenv()

if "__main__" == __name__:
    openai_api_key = os.getenv("OPENAI_API_KEY")

    tweets = pd.read_json("apis/x/tweets.json").to_dict()
    response = api_connection.gerar_relatorio(openai_api_key,tweets_json=tweets)
    output_hour = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")

    if not os.path.exists("apis/response_api"):
        os.makedirs("apis/response_api")
    with open(f"apis/response_api/analysis_{output_hour}.json", mode="w") as txt:
        txt.write(str(response))
    print(response)