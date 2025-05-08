import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database.mongo import db
import logging
from fastapi.responses import JSONResponse

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
    try:
        # Gerar um ID único para o usuário
        user_id = str(uuid.uuid4())
        
        # Converter o modelo para dicionário
        user_data = userCreate.model_dump()
        user_data["user_id"] = user_id
        
        # Verificar se já existe um usuário com o mesmo email
        existing_user = await db["users"].find_one({"email": userCreate.email})
        if existing_user:
            user_data = await db["users"].find_one({"email": userCreate.email})
            return JSONResponse(
                status_code=200,
                content={"message": "Usuário já cadastrado", "data": {"user_id": user_data["user_id"]}}
            )
        
        # Inserir o novo usuário no banco de dados
        await db["users"].insert_one(user_data)
        
        # Remover a senha (se existir) antes de retornar

            
        return {"message": "Usuário criado com sucesso", "data": user_data}
        
    except ConnectionError:
        # Erro de conexão com o MongoDB
        logging.error("Erro de conexão com o MongoDB", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Serviço de banco de dados indisponível. Tente novamente mais tarde."
        )
    except Exception as e:
        # Log detalhado para depuração
        logging.error(f"Erro ao criar usuário: {str(e)}", exc_info=True)
        
        # Resposta genérica para o cliente
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro ao processar sua solicitação. Entre em contato com o suporte."
        )
    
@router.get("/user/{email}")
async def get_user(email: str):
    user = await db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


