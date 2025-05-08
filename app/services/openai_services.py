import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# colocar a lib async da openai
# criar uma nova colections de messages no mongo para ele persistir as mensagens da conversa



def get_ai_response( messages) -> str:
   
    response =  client.chat.completions.create(
        model="gpt-3.5-turbo",  # ou outro modelo disponível
        messages=messages
    )
    return response.choices[0].message.content