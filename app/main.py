
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routers import chat, news, user, favorites
from app.services.log.logger import LoggerMiddleware


import os

openai_api_key = os.getenv("OPENAI_API_KEY")
mongodb_url = os.getenv("MONGODB_URL")

app = FastAPI(
    title="News AI API",
    description="API para chat, notícias, usuários e favoritos",
    version="1.0.0"
)


app.include_router(chat.router,  tags=["Chat"])
app.include_router(user.router,  tags=["User"])
app.include_router(favorites.router,  tags=["Favorites"])
app.include_router(news.router,  tags=["News"])

@app.get("/")
def read_root():
    return RedirectResponse(url="/redoc")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)