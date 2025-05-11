from datetime import datetime
from app.models.chat import ChatRequest
from app.services.news.news_services import get_text_news

def create_user_message(message):
    return {
        "role": "user",
        "content": message,
        "timestamp": datetime.now()
    }

def create_assistant_message_for_db(ai_response):
    return {
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.now()
    }

def prepare_messages(conversation, request):
    if request.url:
        system_content = "Você é um assistente de IA chamado Scooby que responde perguntas sobre notícias. Você recebeu o conteúdo de uma notícia específica. USE APENAS ESTE CONTEÚDO para responder às perguntas do usuário sobre esta notícia. NÃO use a ferramenta get_news quando estiver respondendo sobre a notícia já fornecida."
    else:
        system_content = "Você é um assistente de IA chamado Scooby que responde perguntas sobre notícias. Use a ferramenta get_news quando o usuário quiser informações sobre notícias específicas que não foram fornecidas no contexto."
    
    messages = [{"role": "system", "content": system_content}]
    
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