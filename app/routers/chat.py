
from fastapi import APIRouter
from app.models.chat import ChatRequest
from app.services.openAi.openai_services import call_openai_with_tools
from app.database.mongo import db
from app.services.chat import chat as chat_service

router = APIRouter()

# PEDI O CHAT PARA COMENTAR CADA FUNCAO PARA EU NAO FICAR PERDIDO

@router.post("/chat")
async def chat(request: ChatRequest):
    return await chat_service(request)

@router.get("/chat/{user_id}")
async def get_chat(user_id: str):
    history = []
    async for chat in db.chats.find({"user_id": user_id}, {"_id": 0}):
        history.append(chat)
    return history

