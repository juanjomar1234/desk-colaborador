#!/usr/bin/env python
import os
import sys
import logging
import traceback

# Configurar logging
logging.basicConfig(
    filename='/home/u396608776/domains/uno14.trading/public_html/portalcolaborador/debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Log del entorno
    logger.debug("=== Starting Application ===")
    logger.debug(f"Python Version: {sys.version}")
    logger.debug(f"Python Path: {sys.path}")
    logger.debug(f"Working Directory: {os.getcwd()}")
    logger.debug(f"Script Name: {os.environ.get('SCRIPT_NAME', 'Not Set')}")
    logger.debug(f"Request Method: {os.environ.get('REQUEST_METHOD', 'Not Set')}")
    logger.debug(f"Query String: {os.environ.get('QUERY_STRING', 'Not Set')}")
    
    # Configurar el path de Python
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, base_dir)
    logger.debug(f"Base Directory: {base_dir}")
    
    # Importar la aplicación
    from frontend_service.wsgi import app as application
    logger.debug("Application imported successfully")
    
    # Ejecutar la aplicación
    if __name__ == '__main__':
        from wsgiref.handlers import CGIHandler
        logger.debug("Starting CGI Handler")
        CGIHandler().run(application)

except Exception as e:
    logger.error(f"Error: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    print("Content-Type: text/plain\n")
    print(f"Error: {str(e)}")
    print("\nTraceback:")
    print(traceback.format_exc()) 