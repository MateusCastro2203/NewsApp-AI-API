import uuid
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.database.mongo import db
import logging
import json
from fastapi.responses import JSONResponse
from app.services.log.logger import logger

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str

class User(BaseModel):
    user_id: str
    name: str
    email: str

@router.post("/user")
async def create_user(userCreate: UserCreate, request: Request):
    # Gera request_id para a solicitação atual
    request_id = str(uuid.uuid4())

    # Log no formato compatível com Railway
    logger.info(
        "Tentativa de criação de usuário",
        extra={
            "request_id": request_id,
            "email": userCreate.email,
            "method": request.method,
            "path": request.url.path,
            "headers": {
                "content-type": request.headers.get("content-type", ""),
                "user-agent": request.headers.get("user-agent", ""),
                "host": request.headers.get("host", ""),
                "request-method": request.method  # Redundante para depuração
            }
        }
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
            
            logger.info(
                "Usuário já cadastrado", 
                extra={
                    "request_id": request_id,
                    "user_id": user_dict["user_id"],
                    "status": "existing_user"
                }
            )
            
            return JSONResponse(
                status_code=200,
                content={"message": "Usuário já cadastrado", "data": {"user_id": user_dict["user_id"]}}
            )
        
        # Inserir o novo usuário no banco de dados
        await db["users"].insert_one(user_data)
        
        # Certifique-se de que não há _id no dict que será retornado
        if "_id" in user_data:
            del user_data["_id"]
        
        logger.info(
            "Usuário criado com sucesso", 
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "status": "success"
            }
        )
            
        return {"message": "Usuário criado com sucesso", "data": user_data}
        
    except ConnectionError as ce:
        # Erro de conexão com o MongoDB
        logger.error(
            "Erro de conexão com o MongoDB",
            extra={
                "request_id": request_id,
                "error_type": "connection_error",
                "error_details": str(ce)
            },
            exc_info=True
        )
        
        raise HTTPException(
            status_code=503,
            detail="Serviço de banco de dados indisponível. Tente novamente mais tarde."
        )
    except Exception as e:
        logger.error(
            "Erro ao criar usuário",
            extra={
                "request_id": request_id, 
                "email": userCreate.email,
                "error_type": type(e).__name__,
                "error_details": str(e)
            },
            exc_info=True
        )
        
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro ao processar sua solicitação."
        )
    
@router.get("/user/{email}")
async def get_user(email: str, request: Request):
    # Gera request_id para a solicitação atual
    request_id = str(uuid.uuid4())
    
    logger.info(
        "Buscando usuário por email",
        extra={
            "request_id": request_id,
            "email": email,
            "method": request.method
        }
    )
    
    user = await db["users"].find_one({"email": email})
    if not user:
        logger.info(
            "Usuário não encontrado",
            extra={
                "request_id": request_id,
                "email": email,
                "status": "not_found"
            }
        )
        
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if "_id" in user:
        user["_id"] = str(user["_id"])
    
    logger.info(
        "Usuário encontrado com sucesso",
        extra={
            "request_id": request_id,
            "email": email,
            "user_id": user.get("user_id", ""),
            "status": "success"
        }
    )
    
    return user