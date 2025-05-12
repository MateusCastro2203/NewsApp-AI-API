import os
from typing import List
import httpx
import requests
from bs4 import BeautifulSoup

from app.models.news import NewsItem, NewsRequest

def get_text_news(url: str) -> str:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Encontra o conteúdo principal
        article = soup.find("article") or soup.find("div", class_="article") or soup.find("main") or soup.find("div", class_="content") or soup.find("div", class_="article-content")
        
        if article:
            # Remove elementos indesejados
            for tag in article.find_all(["script", "style", "iframe", "button"]):
                tag.decompose()
            
            # Extrai o texto
            content = article.get_text(separator="\n", strip=True)
            return content
        else:
            # Fallback: usa o body se não encontrar artigo específico
            body_text = soup.body.get_text(separator="\n", strip=True)
            # Limita o tamanho para evitar exceder o limite de tokens
            return body_text[:5000]
            
    except Exception as e:
        return f"Erro ao processar a notícia: {str(e)}"
    
async def fetch_news_with_category(category: List[str]) -> List[NewsRequest]:
    try:
        # Construir a URL com os parâmetros
        base_url = os.getenv("NEWS_API_URL")
        params = {
            "category": ",".join(category),
            "language": "pt",
            "apikey": os.getenv("NEWS_API_KEY")  # Note: changed from apiKey to apikey
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
       
        data = response.json()
        
        if data.get("status") == "success":
            return format_api_news(data.get("results", []))
        return []
        
    except Exception as e:
        return []
    
async def fetch_news_with_query(query: str) -> List[NewsRequest]:
    try:
        base_url = os.getenv("NEWS_API_URL")
        params = {
            "q": query,
            "language": "pt",
            "apikey": os.getenv("NEWS_API_KEY")
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
        
        if data.get("status") == "success":
            return format_api_news(data.get("results", []))
        return []
        
    except Exception as e:
        print(f"Erro ao buscar notícias: {str(e)}")
        return []
    

def format_api_news(api_results) -> List[NewsItem]:
    news_list = []

    for item in api_results:
        try:
            news_item = NewsItem(
                id=item.get("article_id"),
                title=item["title"],
                description=item["description"],
                content=item.get("content"),
                url=item.get("link", ""),
                source_name=item.get("source_id", "Fonte desconhecida"),
                source_url=item.get("source_url"),
                image_url=item.get("image_url"),
                published_at=item.get("pubDate"),
                category=item.get("category"),
                source_type="api"
            )
            news_list.append(news_item)
        except Exception as e:
            print(f"Erro ao formatar notícia: {str(e)}")
            continue

    return news_list
