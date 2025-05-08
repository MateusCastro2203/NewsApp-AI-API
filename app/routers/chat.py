from fastapi import APIRouter
from app.models.chat import ChatRequest
from app.services.openai_services import get_ai_response
from app.services.news_services import get_text_news
from app.database.mongo import db
from datetime import datetime
import uuid


router = APIRouter()

chat_history = {}

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        # verifica se o id da conversa existe
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # verifica se a conversa existe
        conversation = await db["conversation"].find_one({"conversation_id": conversation_id})

        # se a conversa não existir, cria uma nova conversa
        if not conversation:
            conversation = {
                "conversation_id": conversation_id,
                "user_id": request.user_id,
                "messages": []
            }

        # adiciona a mensagem do usuário à conversa
        now = datetime.now()
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": now
        }
        
        # adiciona a mensagem do sistema à conversa
        messages = [{"role": "system", "content": "Você é um assistente de IA chamado Scooby que responde perguntas sobre notícias."}]
        
        # se a url fornecida pelo usuário for uma url de notícia, extrai o conteúdo da notícia
        article_content = ""
        if request.url:
            article_content =  get_text_news(request.url)
            context_message = {
                "role": "user", 
                "content": f"A seguir está o conteúdo da notícia que o usuário está se referindo:\n\n{article_content}\n\nResponda considerando este contexto."
            }
            messages.append(context_message)

        # adiciona as mensagens anteriores à conversa
        for msg in conversation["messages"]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # adiciona a mensagem do usuário atual à conversa
        messages.append({"role": "user", "content": request.message})

        # obtém a resposta da IA
        ai_response = get_ai_response(messages)

        # adiciona a mensagem do assistente à conversa
        assistant_message = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now()
        }

        # atualiza a conversa no banco de dados
        await db["conversation"].update_one(
        {"conversation_id": conversation_id},
        {
            "$set": {
                "user_id": request.user_id, 
                "conversation_id": conversation_id,
                },
            "$push": {
                "messages": {
                    "$each": [user_message, assistant_message]
                }
            }

            },
        upsert=True
        )

        return{
            "response": ai_response,
            "conversation_id": conversation_id
        }
        
    except Exception as e:
        return {"error": str(e)}
   

@router.get("/chat/{user_id}")
async def get_chat(user_id: str):
    history = []
    async for chat in db.chats.find({"user_id": user_id}, {"_id": 0}):
        history.append(chat)
    return history