import json
import uuid
from app.models.chat import ChatRequest
from app.services.chat.conversation_service import get_or_create_conversation, update_conversation
from app.services.chat.message_service import create_user_message, create_assistant_message_for_db, prepare_messages
from app.services.chat.tool_service import define_tools, has_tool_call, find_tool_call, get_news_with_query, search_web
from app.services.openAi.openai_services import call_openai_with_tools

async def chat(request):
    try:
        # Inicialização da conversa
        conversation_id = request.conversation_id or str(uuid.uuid4())
        conversation = await get_or_create_conversation(conversation_id, request.user_id)
        
        # Preparação das mensagens
        user_message = create_user_message(request.message)
        messages = prepare_messages(conversation, request)
        
        # Definição de tools disponíveis para a IA
        tools = define_tools()
        
        # Consulta à OpenAI com suporte a tools
        response = await call_openai_with_tools(messages, tools)
        assistant_message = response.choices[0].message
        ai_response = assistant_message.content or ""
        
        # Verifica se a IA quer usar a tool para buscar notícias
        if has_tool_call(assistant_message, "fetch_news_with_query"):
            tool_call = find_tool_call(assistant_message, "fetch_news_with_query")
            news = await get_news_with_query(tool_call)
            if not news:
                web_tool_call = {
                    "function": {
                        "arguments": json.dumps({"query": tool_call.function.arguments})
                    }
                }
                web_result = await search_web(web_tool_call)
                return {
                    "response": ai_response,
                    "conversation_id": conversation_id,
                    "api_result": web_result,
                    "tool_call": True
                }
            return {
                "response": ai_response,
                "conversation_id": conversation_id,
                "api_result": news,
                "tool_call": True
            }
        # Verifica se a IA quer usar diretamente a tool search_web
        elif has_tool_call(assistant_message, "search_web"):
            tool_call = find_tool_call(assistant_message, "search_web")
            api_result = await search_web(tool_call)
            return {
                "response": ai_response,
                "conversation_id": conversation_id,
                "api_result": api_result,
                "tool_call": True
            }
        
        # Fluxo normal (sem uso de tools)
        assistant_message_db = create_assistant_message_for_db(ai_response)
        
        # Salva a conversa no banco de dados
        await update_conversation(conversation_id, request.user_id, user_message, assistant_message_db)
        
        return {
            "response": ai_response,
            "conversation_id": conversation_id,
            "tool_call": False
        }
        
    except Exception as e:
        return {"error": str(e)}