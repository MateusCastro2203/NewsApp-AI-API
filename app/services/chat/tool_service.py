import json
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
                "description": "Pesquisa na internet a melhor e mais atualizada fonte sobre o assunto fornecido pelo usuário",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Pergunta ou assunto a ser pesquisado na web"
                        }
                    },
                    "required": ["query"]
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
    params = get_tool_call_arguments(tool_call)

    query = ""
    if "query" in params:
        query = params["query"]
    elif "tema" in params:
        query = params["tema"]

    if isinstance(query, str) and query.startswith('{') and query.endswith('}'):
        try:
            query_dict = json.loads(query)
            if "tema" in query_dict:
                query = query_dict["tema"]
            elif "query" in query_dict:
                query = query_dict["query"]
        except:
            pass
    
    result =  await search_web_serper(query)
    return result


