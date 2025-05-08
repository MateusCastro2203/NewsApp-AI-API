from fastapi import FastAPI
from app.routers import chat, user, favorites
from app.services.logger import LoggerMiddleware
import os

openai_api_key = os.getenv("OPENAI_API_KEY")
mongodb_url = os.getenv("MONGODB_URL")

app = FastAPI()

app.add_middleware(LoggerMiddleware)

app.include_router(chat.router)
app.include_router(user.router)
app.include_router(favorites.router)

@app.get("/")
def read_root():
    return {"message": "NewsBot API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)