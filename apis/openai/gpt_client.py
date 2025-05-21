import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4.1-mini"

def analyze_chunk_to_csv(chunk: str) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não definido")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        "Você é um analista de perfis de redes sociais.\n"
        "Analise o texto abaixo (tweets) e extraia:\n"
        "1. Principais interesses (separe por vírgula)\n"
        "2. Tom de voz (uma frase)\n"
        "3. Tópicos recorrentes (separe por vírgula)\n"
        "Responda COM UMA ÚNICA LINHA CSV sem cabeçalho: interesses,tom,topicos\n\n"
        f"{chunk}\n"
    )
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Analista de perfis de Twitter."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 600
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()
