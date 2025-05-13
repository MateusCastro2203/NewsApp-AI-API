# app/services/utils/formatters.py
from typing import List
from app.models.news import NewsItem, NewsRequest

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


