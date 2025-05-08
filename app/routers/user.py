import uuid
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.database.mongo import db
import logging
from fastapi.responses import JSONResponse
from app.services.logger import logger

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str

class User(BaseModel):
    user_id: str
    name: str
    email: str

request_id =  getattr(Request.state, "request_id", str(uuid.uuid4()))

@router.post("/user")
async def create_user(userCreate: UserCreate):

    logger.info(
        f"Tentativa de criação de usuário com email: {userCreate.email}",
        extra={"request_id": request_id, "email": userCreate.email}
    )
    
    try:
        # Gerar um ID único para o usuário
        user_id = str(uuid.uuid4())
        
        # Converter o modelo para dicionário
        user_data = userCreate.model_dump()
        user_data["user_id"] = user_id
        
        # Verificar se já existe um usuário com o mesmo email
        existing_user = await db["users"].find_one({"email": userCreate.email})
        if existing_user:
            # Convertendo ObjectId para string e criando um novo dicionário sem _id
            user_dict = {
                "user_id": existing_user.get("user_id", ""),
                "email": existing_user.get("email", ""),
                "name": existing_user.get("name", "")
            }
            
            return JSONResponse(
                status_code=200,
                content={"message": "Usuário já cadastrado", "data": {"user_id": user_dict["user_id"]}}
            )
        
        # Inserir o novo usuário no banco de dados
        await db["users"].insert_one(user_data)
        
        # Certifique-se de que não há _id no dict que será retornado
        if "_id" in user_data:
            del user_data["_id"]
            
        return {"message": "Usuário criado com sucesso", "data": user_data}
        
    except ConnectionError:
        # Erro de conexão com o MongoDB
        logging.error("Erro de conexão com o MongoDB", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Serviço de banco de dados indisponível. Tente novamente mais tarde."
        )
    except Exception as e:
       
        logger.error(
            f"Erro ao criar usuário: {str(e)}",
            extra={"request_id": request_id, "email": userCreate.email},
            exc_info=True
        )
        
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro ao processar sua solicitação."
        )
    
    
@router.get("/user/{email}")
async def get_user(email: str):
    user = await db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
   
    if "_id" in user:
        user["_id"] = str(user["_id"])
    
    return user


