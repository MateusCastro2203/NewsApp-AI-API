from fastapi import FastAPI
from app.routers import chat, user, favorites

app = FastAPI()

app.include_router(chat.router)
app.include_router(user.router)
app.include_router(favorites.router)

@app.get("/")
def read_root():
    return {"message": "NewsBot API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)