import logging
import os
import sys

# Ensure config can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_logger(name='reel_factory'):
    from config import LOG_DIR, LOG_FILE
    
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
        
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
        fh.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
    return logger

class AppLogger:
    _logger = None
    
    @classmethod
    def get_logger(cls):
        if cls._logger is None:
            cls._logger = setup_logger()
        return cls._logger

def get_logger(name='reel_factory'):
    return setup_logger(name)
