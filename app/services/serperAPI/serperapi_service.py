import os
from typing import List
from dotenv import load_dotenv
import uuid
from datetime import datetime
import httpx
import asyncio

from app.models.news import NewsItem
from app.services.news.news_services import format_api_news
from app.core.utils.get_news_image import get_main_image_from_url

load_dotenv()

def format_serper_results(search_results) -> List[NewsItem]:
    news_list = []

    for item in search_results:
        try:
            # Gera um ID único para o resultado da busca
            item_id = str(uuid.uuid4())
            
            # Processa a data (se existir)
            published_at = None
            if "date" in item:
                # Converte datas aproximadas como "há 2 dias" para datetime (simplificado)
                published_at = datetime.now()
            
            image_url = get_main_image_from_url(item.get("link", ""))
            
            news_item = NewsItem(
                id=item_id,
                title=item.get("title", "Sem título"),
                description=item.get("snippet", "Sem descrição"),
                content=None,  # Não temos o conteúdo completo da busca
                url=item.get("link", ""),
                source_name=item.get("link", "").split("/")[2] if "link" in item else "Web",  # Extrai o domínio da URL
                source_url=item.get("link", ""),
                image_url=image_url,
                published_at=published_at,
                category=None,  # Não temos categorias nos resultados de busca
                source_type="web"  # Marca como resultado da web
            )
            news_list.append(news_item)
        except Exception as e:
            print(f"Erro ao formatar resultado da web: {str(e)}")
            continue

    return news_list

async def search_web_serper(query) -> List[NewsItem]:
    params = {
        "q": query,
        "gl": "br",
        "hl": "pt-BR",
        "tbs": "qdr:w",
        "type": "search",
        "engine": "google",
        "num": 10,     
        "include_images": True,  
    }
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    url = os.getenv("SERPER_URL")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            results = []

            if "organic" in data:
                organic_results = format_serper_results(data["organic"])
                results.extend(organic_results)
            return results
            
    except Exception as e:
        print(f"Erro ao buscar no SerperAPI: {str(e)}")
        return []

