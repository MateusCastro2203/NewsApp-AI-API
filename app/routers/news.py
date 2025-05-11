from fastapi import APIRouter
from typing import List
from app.services.news.news_services import fetch_news_with_category, fetch_news_with_query


router = APIRouter()

@router.post("/news")
async def get_news(category: List[str]):
    return await fetch_news_with_category(category)

@router.post("/news/query")
async def get_news_with_query(query: str):
    return await fetch_news_with_query(query)




