import json

from fastapi import logger
from app.services.favoritesNews.favorites_services import get_news_for_favorites_db
from app.services.news.news_services import fetch_news_with_query
from app.services.openAi.openai_services import call_openai_with_parameters_search_web
from app.services.serperAPI.serperapi_service import search_web_serper

def define_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "fetch_news_with_query",
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
        },
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Pesquisa na internet informações atualizadas sobre o assunto fornecido pelo usuário. Retorna resultados completos com título, descrição, conteúdo, imagens, categorias e data de publicação.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Pergunta ou assunto a ser pesquisado na web. Seja específico para obter resultados mais relevantes."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_news_for_favorites",
                "description": "Busca notícias favoritas do usuário no banco de dados",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string", 
                            "description": "ID do usuário para buscar as noticias favoritas"
                            }
                    },
                    "required": ["user_id"]
                }
            }
        }
    ]

def has_tool_call(assistant_message, tool_name):
    if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            if tool_call.function.name == tool_name:
                return True
    return False

def find_tool_call(assistant_message, tool_name):
    for tool_call in assistant_message.tool_calls:
        if tool_call.function.name == tool_name:
            return tool_call
    return None


def get_tool_call_arguments(tool_call):
    # Tenta acessar como objeto, se não der tenta como dict
    try:
        return json.loads(tool_call.function.arguments)
    except AttributeError:
        return json.loads(tool_call["function"]["arguments"])

async def get_news_with_query(tool_call):
    params = get_tool_call_arguments(tool_call)
    result = await fetch_news_with_query(params["tema"])
    return result

async def search_web(tool_call):
    print(f"Recebido tool_call para search_web: {tool_call}")
    params = get_tool_call_arguments(tool_call)
    print(f"Parâmetros extraídos: {params}")

    query = ""
    if "query" in params:
        query = params["query"]
    elif "tema" in params:
        query = params["tema"]
    
    print(f"Query inicial: '{query}'")
    
    # Se a query for um JSON string, tenta extrair o valor de dentro
    if isinstance(query, str):
        # Remove quotes extras no início e fim
        query = query.strip('"\'')
        
        # Tenta extrair do JSON
        if query.startswith('{') and query.endswith('}'):
            try:
                query_dict = json.loads(query)
                if "tema" in query_dict:
                    query = query_dict["tema"]
                elif "query" in query_dict:
                    query = query_dict["query"]
            except json.JSONDecodeError as e:
                logger.info(
                    f"Erro ao decodificar JSON: {e}",
                    extra={"query": query}
                )
                return []
    
    result = await search_web_serper(query)
    return result


async def get_news_for_favorites(tool_call):
    params = get_tool_call_arguments(tool_call)
    result = await get_news_for_favorites_db(params["user_id"])
    return result
