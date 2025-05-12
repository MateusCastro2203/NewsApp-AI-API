from fastapi import APIRouter
from typing import List
from app.models.news import NewsItem
from app.services.news.news_services import fetch_news_with_category, fetch_news_with_query


router = APIRouter()

@router.get("/news", response_model=List[NewsItem])
async def get_news(category: List[str]):
    return await fetch_news_with_category(category)

@router.get("/news/query", response_model=List[NewsItem])
async def get_news_with_query(query: str):
    return await fetch_news_with_query(query)




