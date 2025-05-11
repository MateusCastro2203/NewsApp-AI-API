import os
from dotenv import load_dotenv

import httpx

load_dotenv()

async def search_web_serper(query):
    params = {
        "q": query,
        "gl": "br",
        "hl": "pt-BR",
        "tbs": "qdr:w"
    },
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    url = os.getenv("SERPER_URL")
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=params, headers=headers)
        data = resp.json()
        return data

