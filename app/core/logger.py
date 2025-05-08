import logging
import json

import time


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "path": record.pathname,
            "line": record.lineno
        }

        if hasattr(record, 'request_id'):
            log_data["request_id"] = record.request_id

        if hasattr(record, 'user_id'):
            log_data["user_id"] = record.user_id
            
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)
    
def setup_logger():
    logger = logging.getLogger("newsbot")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

    return logger

logger = setup_logger()
