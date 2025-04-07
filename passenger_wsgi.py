import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    filename='/home/u396608776/domains/uno14.trading/public_html/portalcolaborador/passenger.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    logger.debug("=== Starting Passenger WSGI ===")
    logger.debug(f"Current Python: {sys.executable}")
    logger.debug(f"Current Path: {sys.path}")
    
    # Configurar el intérprete de Python
    INTERP = "/home/u396608776/domains/uno14.trading/public_html/portalcolaborador/venv/bin/python"
    if sys.executable != INTERP:
        logger.debug(f"Switching to interpreter: {INTERP}")
        os.execl(INTERP, INTERP, *sys.argv)

    # Configurar paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Adding to path: {current_dir}")
    sys.path.insert(0, current_dir)

    # Importar la aplicación
    logger.debug("Importing application...")
    from frontend_service.wsgi import app as application
    logger.debug("Application imported successfully")

except Exception as e:
    logger.error(f"Error in passenger_wsgi.py: {str(e)}")
    logger.error(f"Python path: {sys.path}")
    raise 