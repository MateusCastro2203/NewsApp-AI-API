from fastapi import APIRouter, Query, Body
from typing import List
from app.models.news import NewsItem
from app.services.favoritesNews.favorites_services import add_favorite_news_item, get_favorite_news_topic, add_favorite_news_topic, get_news_for_favorites_db
from app.services.news.news_services import fetch_news_with_category, fetch_news_with_query


router = APIRouter()

@router.post("/news", response_model=List[NewsItem])
async def get_news(
    category: List[str] = Body(
        ...,
        description="List of news categories to fetch",
        example=["business", "technology", "sports"]
    )
):
    """
    Fetch news articles by category.
    
    - **category**: List of category names provided in the request body as a JSON array
    
    Example call:
    ```
    POST /news
    
    ["business", "technology", "sports"]
    ```
    """
    return await fetch_news_with_category(category)

@router.post("/news/query", response_model=List[NewsItem])
async def get_news_with_query(
    query: str = Body(
        ...,
        description="Search query to find news articles",
        example="climate change"
    )
):
    """
    Search for news articles using a specific query.
    
    - **query**: Search term provided in the request body as a string
    
    Example call:
    ```
    POST /news/query
    
    "climate change"
    ```
    """
    return await fetch_news_with_query(query)


@router.get("/news/favorites/topic", response_model=List[NewsItem])
async def get_news_with_favorites(
    user_id: str = Query(
        ...,
        description="User ID to fetch favorites for",
        example="123"
    )
):
    """
    Get all favorite news items for a specific user.
    
    - **user_id**: Must be provided as a query parameter in the URL (e.g., ?user_id=123)
    
    Example call:
    ```
    GET /news/favorites?user_id=123
    ```
    """
    return await get_favorite_news_topic(user_id)

@router.post("/news/favorites/topic/add", response_model=List[NewsItem])
async def poost_add_favorite_news(
    user_id: str = Query(
        ...,  # ... means the parameter is required
        description="User ID to add favorites to (passed in URL query string)",
        example="/news/favorites/add?user_id=123"
    ), 
    news: List[str] = Body(
        ...,
        description="List of news IDs to add as favorites",
        example=["crime", "top"]
    )
):
    """
    Add news items to a user's favorites list.
    
    - **user_id**: Must be provided as a query parameter in the URL (e.g., ?user_id=abc123)
    - **news**: List of news IDs to favorite, provided in the request body as a JSON array
    
    Example call:
    ```
    POST /news/favorites/add?user_id=12343
    
    ["crime", "top"]
    ```
    """
    return await add_favorite_news_topic(user_id, news)

@router.post("/news/favorites/item/add", response_model=List[NewsItem])
async def post_add_favorite_news_item(
    user_id: str = Query(
        ...,
        description="User ID to add favorites to (passed in URL query string)",
        example="/news/favorites/add?user_id=123"
    ), 
    news: NewsItem = Body(
        ...,
        description="News item to add as a favorite",
    )
):
    """
    Add a news item to a user's favorites list.
    
    - **user_id**: Must be provided as a query parameter in the URL (e.g., ?user_id=abc123)
    - **news**: News item to favorite, provided in the request body

    Example call:
    ```
    POST /news/favorites/item/add?user_id=12343
    
    {
        "id": "12343",
        id: str  # ID único da notícia
        title: str  # Título
        description: Optional[str] = None  # Descrição curta
        content: Optional[str] = None  # Conteúdo completo, quando disponível
        url: str  # Link para a notícia
        source_name: str  # Nome da fonte (ex: "G1", "CNN", etc)
        source_url: Optional[str] = None  # URL da fonte
        image_url: Optional[str] = None  # URL da imagem principal
        published_at: Optional[datetime] = None  # Data de publicação
        category: Optional[List[str]] = None  # Categorias
        source_type: str = Field(..., description="'api' para notícias da API, 'web' para buscas na web")

    }
    ```
    """
    return await add_favorite_news_item(user_id, news)


@router.get("/news/favorites/item", response_model=List[NewsItem])
async def get_news_for_favorites(
    user_id: str = Query(
        ...,
        description="User ID to fetch favorites for",
        example="123"
    )
):
    return await get_news_for_favorites_db(user_id)


