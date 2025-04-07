#!/usr/bin/env python
import sys
import logging
import os

# Configurar logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Log del path de Python y variables de entorno
    logger.debug(f"Python path: {sys.path}")
    logger.debug(f"Current working directory: {os.getcwd()}")
    
    from frontend_service.wsgi import app as application
    logger.debug("Frontend service loaded successfully")
except Exception as e:
    logger.error(f"Error loading application: {str(e)}")
    raise 