import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database.mongo import db

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str

class User(BaseModel):
    user_id: str
    name: str
    email: str

@router.post("/user")
async def create_user(userCreate: UserCreate):
    user_id = str(uuid.uuid4())
    user_data = userCreate.model_dump()
    user_data["user_id"] = user_id
    try:
        if await db["users"].find_one({"email": userCreate.email}):
            return {"message": "Usuário já existe", "data": user_data}
        await db["users"].insert_one(user_data)
        return {"message": "Usuário criado com sucesso", "data": user_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/user/{email}")
async def get_user(email: str):
    user = await db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


