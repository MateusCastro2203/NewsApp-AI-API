import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from app.core.logger import logger

async def log_request(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.info(
        f"Iniciando requisição {request_id}", 
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
        }
    )
    
    start_time = time.time()

    try:
        # Processa a requisição
        response = await call_next(request)
        
        # Log de finalização
        process_time = time.time() - start_time
        logger.info(
            f"Finalizada {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000)
            }
        )
        return response
        
    except Exception as e:
        # Log de erro
        logger.error(
            f"Erro ao processar {request.method} {request.url.path}: {str(e)}",
            extra={"request_id": request_id},
            exc_info=True
        )
        raise

logger_middleware = Middleware(log_request)

