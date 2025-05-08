import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.getenv("MONGO_URL")
if mongo_url and "mongodb+srv" in mongo_url:
    # Adicione parâmetros TLS se não existirem já na URL
    if "?" in mongo_url:
        if "&tls=true" not in mongo_url and "&tlsInsecure=false" not in mongo_url:
            mongo_url += "&tls=true&tlsAllowInvalidCertificates=false"
    else:
        mongo_url += "?tls=true&tlsAllowInvalidCertificates=false"

client = AsyncIOMotorClient(mongo_url)
db = client["newsbot"]