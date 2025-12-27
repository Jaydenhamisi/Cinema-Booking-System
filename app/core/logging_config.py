"""
Logging setup for Cinema Booking System.
Provides structured JSON logs and colored console output.
"""

import logging
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from contextvars import ContextVar
import uuid


# Context variable for request tracing
request_id_var: ContextVar[str] = ContextVar('request_id', default=None)


def get_request_id() -> str:
    """Get current request ID"""
    return request_id_var.get()


def set_request_id(request_id: str = None) -> str:
    """Set request ID for current context"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing and analysis"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),  # Fixed deprecated warning
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add request ID if available
        request_id = get_request_id()
        if request_id:
            log_data['request_id'] = request_id
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'context'):
            log_data['context'] = record.context
            
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored output for console (human-readable)"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(log_level='DEBUG'):
    """
    Set up logging with both console and file handlers.
    
    Creates:
    - Colored console output for development
    - JSON file logs for debugging (debug_YYYYMMDD.log)
    - Structured info logs (app_YYYYMMDD.log)
    - Error-only logs (errors.log)
    """
    
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Console handler (colored, human-readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredConsoleFormatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler - DEBUG level (everything)
    debug_file = log_dir / f'debug_{datetime.now().strftime("%Y%m%d")}.log'
    debug_handler = logging.FileHandler(debug_file)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(JSONFormatter())
    
    # File handler - INFO level (less noise)
    info_file = log_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
    info_handler = logging.FileHandler(info_file)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(JSONFormatter())
    
    # File handler - ERROR level (only errors)
    error_file = log_dir / 'errors.log'
    error_handler = logging.FileHandler(error_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    
    # Add all handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(debug_handler)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(error_handler)
    
    # Silence noisy libraries
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    
    return root_logger