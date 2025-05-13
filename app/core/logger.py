import logging
import sys
import json
from datetime import datetime

class RailwayFormatter(logging.Formatter):
    """Formatador que gera logs compatíveis com Railway"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        # Adiciona campos adicionais se existirem
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Adiciona informações de exceção se existirem
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logger():
    # Criar logger
    logger = logging.getLogger("newsbot")
    logger.setLevel(logging.INFO)
    
    # Limpar handlers existentes
    if logger.handlers:
        logger.handlers.clear()
    
    # Criar handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RailwayFormatter())
    
    # Adicionar handler ao logger
    logger.addHandler(handler)
    
    return logger

# Criar e configurar o logger
logger = setup_logger()