import json
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest
from app.services.openai_services import get_ai_response, call_openai_with_tools
from app.services.news_services import get_text_news
from app.database.mongo import db

router = APIRouter()

# PEDI O CHAT PARA COMENTAR CADA FUNCAO PARA EU NAO FICAR PERDIDO

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Inicialização da conversa
        conversation_id = request.conversation_id or str(uuid.uuid4())
        conversation = await get_or_create_conversation(conversation_id, request.user_id)
        
        # Preparação das mensagens
        user_message = create_user_message(request.message)
        messages = prepare_messages(conversation, request, user_message)
        
        # Definição de tools disponíveis para a IA
        tools = define_tools()
        
        # Consulta à OpenAI com suporte a tools
        response = await call_openai_with_tools(messages, tools)
        assistant_message = response.choices[0].message
        ai_response = assistant_message.content or ""
        
        # Verifica se a IA quer usar a tool para buscar notícias
        if has_tool_call(assistant_message, "get_news"):
            tool_call = find_tool_call(assistant_message, "get_news")
            return create_frontend_action_response(tool_call, conversation_id, ai_response)
        
        # Fluxo normal (sem uso de tools)
        assistant_message_db = create_assistant_message_for_db(ai_response)
        
        # Salva a conversa no banco de dados
        await update_conversation(conversation_id, request.user_id, user_message, assistant_message_db)
        
        return {
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

# Funções auxiliares

async def get_or_create_conversation(conversation_id, user_id):
    """Recupera ou cria uma nova conversa."""
    conversation = await db["conversation"].find_one({"conversation_id": conversation_id})
    if not conversation:
        conversation = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "messages": []
        }
    return conversation

def create_user_message(message):
    """Cria objeto de mensagem do usuário."""
    return {
        "role": "user",
        "content": message,
        "timestamp": datetime.now()
    }

def prepare_messages(conversation, request, user_message):
    """Prepara lista de mensagens para envio à OpenAI."""
    messages = [{"role": "system", "content": "Você é um assistente de IA chamado Scooby que responde perguntas sobre notícias."}]
    
    # Adiciona contexto da notícia, se disponível
    if request.url:
        article_content = get_text_news(request.url)
        context_message = {
            "role": "user", 
            "content": f"A seguir está o conteúdo da notícia que o usuário está se referindo:\n\n{article_content}\n\nResponda considerando este contexto."
        }
        messages.append(context_message)
    
    # Adiciona histórico de mensagens
    if "messages" in conversation:
        for msg in conversation["messages"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Adiciona a mensagem atual do usuário
    messages.append({"role": "user", "content": request.message})
    
    return messages

def define_tools():
    """Define as ferramentas disponíveis para a IA."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_news",
                "description": "Busca notícias sobre o assunto fornecido pelo usuário",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tema": {
                            "type": "string",
                            "description": "O tema ou assunto da notícia a ser buscada"
                        }
                    },
                    "required": ["tema"]
                }
            }
        }
    ]

def has_tool_call(assistant_message, tool_name):
    """Verifica se a resposta da IA contém uma chamada para a ferramenta especificada."""
    if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            if tool_call.function.name == tool_name:
                return True
    return False

def find_tool_call(assistant_message, tool_name):
    """Encontra a primeira chamada de ferramenta com o nome especificado."""
    for tool_call in assistant_message.tool_calls:
        if tool_call.function.name == tool_name:
            return tool_call
    return None

def create_frontend_action_response(tool_call, conversation_id, ai_response):
    """Cria resposta para o frontend executar uma ação."""
    params = json.loads(tool_call.function.arguments)
    return {
        "needs_frontend_action": True,
        "action": "get_news",
        "params": params,
        "conversation_id": conversation_id,
        "tool_call_id": tool_call.id,
        "partial_response": ai_response
    }

def create_assistant_message_for_db(ai_response):
    """Cria objeto de mensagem do assistente para salvar no banco de dados."""
    return {
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.now()
    }

async def update_conversation(conversation_id, user_id, user_message, assistant_message_db):
    """Atualiza a conversa no banco de dados."""
    await db["conversation"].update_one(
        {"conversation_id": conversation_id},
        {
            "$set": {
                "user_id": user_id, 
                "conversation_id": conversation_id,
            },
            "$push": {
                "messages": {
                    "$each": [user_message, assistant_message_db]
                }
            }
        },
        upsert=True
    )