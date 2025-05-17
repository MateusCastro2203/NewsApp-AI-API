

from typing import List
import uuid

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.database.mongo import db
from app.models.news import NewsItem
from app.services.news.news_services import fetch_news_with_category
from app.services.news.news_services import get_text_news

async def add_favorite_news_topic(user_id: str, favorite_news: List[str]):
    try:
        # Verificar se o usuário existe
        user = await db["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Verifica se ja existe uma lista de favoritos para o usuario
        if "favorites" not in user:
            user["favorites"] = []
        
        # Adiciona as noticias a lista de favoritos
        user["favorites"].extend(favorite_news)
        
        # Atualiza o usuario na base de dados
        await db["users"].update_one({"user_id": user_id}, {"$set": {"favorites": user["favorites"]}})
        
        return JSONResponse(
                status_code=200,
                content={"message": "Noticias adicionadas aos favoritos com sucesso", "data": {"user_id": user_id}}
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_favorite_news_topic(user_id: str):
    try:
        # Verificar se o usuário existe
        user = await db["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        favorite_news = user.get("favorites", [])
        if not favorite_news:
            raise HTTPException(status_code=404, detail="Nenhuma noticia favorita encontrada")
        
        news = await fetch_news_with_category(favorite_news)
        
        # Return the list of NewsItem objects directly
        return news

    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def add_favorite_news_item(user_id: str, favorite_news: NewsItem):
    try: 
        user = await db["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        existing_favorite = await db["newsFavorites"].find_one({"user_id": user_id})
        if existing_favorite:
            raise HTTPException(status_code=400, detail="Noticia ja favoritada")
        
        news_content = get_text_news(favorite_news.url)
        
        await db["newsFavorites"].insert_one(
            {   
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "news":[
                    {
                        "news_id": favorite_news.id,
                        "news_title": favorite_news.title,
                        "news_description": favorite_news.description,
                        "news_content": news_content
                    }
                ]
            }
        )
        
        return JSONResponse(
            status_code=200,
            content={"message": "Noticia favoritada com sucesso", "data": {"user_id": user_id}}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_news_for_favorites_db(user_id: str):
    try:
        user = await db["users"].find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
        favorite_news = user.get("favorites", [])
        if not favorite_news:
            raise HTTPException(status_code=404, detail="Nenhuma noticia favorita encontrada")
        
        news = await db["newsFavorites"].find_one({"user_id": user_id})
        return news.get("news", [])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
