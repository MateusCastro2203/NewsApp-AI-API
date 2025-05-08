from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database.mongo import db

router = APIRouter()

class Category(BaseModel):
    name: str

class Favorite(BaseModel):
    user_id: str
    news_id: str
    link: str
    title: str
    category: list[Category]

async def verify_db_favorite(favorite: Favorite):
    try:
        existing_news_favorite = await db["favorites"].find_one({"user_id": favorite.user_id, "news_id": favorite.news_id})
        if existing_news_favorite:
            raise HTTPException(status_code=400, detail="Noticia favoritada já cadastrada")
        return existing_news_favorite
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/favorites")
async def add_favorite(favorite: Favorite):
    favorite = await add_favorite(favorite)
    await db["favorites"].insert_one(favorite.model_dump())
    return {"message": "Noticia favoritada cadastrada com sucesso"}

@router.get("/favorites/{user_id}")
async def get_favorites(user_id: str):
    favorites = []
    existing_user = await db["users"].find_one({"user_id": user_id})
    existing_news_favorite = await db["favorites"].find_one({"user_id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if not existing_news_favorite:
        raise HTTPException(status_code=404, detail="Nenhuma noticia favoritada encontrada")
    
    try:
        async for fav in db["favorites"].find({"user_id": user_id}):
            favorites.append(fav)
        return favorites
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

