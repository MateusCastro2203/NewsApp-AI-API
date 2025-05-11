import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# colocar a lib async da openai




def get_ai_response( messages) -> str:
   
    response =  client.chat.completions.create(
        model="gpt-4o",  
        messages=messages
    )
    return response.choices[0].message.content

async def call_openai_with_tools(messages, tools):
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    return response

async def call_openai_with_parameters_search_web(messages):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{"type": "web_search"}],
        tool_choice="auto"
    )
    return response
