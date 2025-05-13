import time
import uuid
import json
import logging
import sys
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configurar logger base para o Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # Formato simples para permitir mensagens JSON
    stream=sys.stdout  # Crucial para o Railway capturar os logs
)

# Criar logger para nossa aplicação
logger = logging.getLogger("newsbot")

class RailwayFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "timestamp": self.formatTime(record, self.datefmt),
            "message": record.getMessage()
        }
        
        # Adicionar extras se existirem
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
            
        # Adicionar exception info se disponível
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

# Configurar o formatador para o logger
for handler in logger.handlers:
    handler.setFormatter(RailwayFormatter())

# Se não houver handlers, adicionar um
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RailwayFormatter())
    logger.addHandler(handler)

class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        
        # Adicionar request_id ao estado da requisição
        request.state.request_id = request_id
        
        # Log de início da requisição
        logger.info(
            "Iniciando requisição", 
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_host": request.client.host if request.client else "unknown",
                "headers": {
                    "user-agent": request.headers.get("user-agent", ""),
                    "content-type": request.headers.get("content-type", "")
                }
            }
        )
        
        start_time = time.time()
        
        try:
            # Processar a requisição
            response = await call_next(request)
            
            # Log de finalização bem-sucedida
            process_time = time.time() - start_time
            logger.info(
                "Requisição finalizada", 
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time * 1000),
                    "success": response.status_code < 400
                }
            )
            
            return response
            
        except Exception as e:
            # Log de erro
            process_time = time.time() - start_time
            logger.error(
                f"Erro ao processar requisição: {str(e)}",
                extra={
                    "request_id": request_id,
                    "process_time_ms": round(process_time * 1000),
                    "error_type": type(e).__name__,
                    "error_details": str(e)
                },
                exc_info=True
            )
            raise