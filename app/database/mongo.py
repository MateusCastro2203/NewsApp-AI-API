import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger("newsbot")


try:
    MONGO_URL = os.getenv("MONGO_URL")
    logger.info(f"Conectando ao MongoDB...")
    client = AsyncIOMotorClient(
        MONGO_URL, 
        serverSelectionTimeoutMS=5000,
        socketTimeoutMS=10000,
    )
    db = client["newsbot"]
    logger.info("Conexão com MongoDB estabelecida com sucesso")


except Exception as e:
    logger.error(f"Erro ao conectar ao MongoDB: {e}")
    db = None
    raise e

