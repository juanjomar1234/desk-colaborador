import os
import sys
import logging

# Configurar logging
logging.basicConfig(
    filename='/home/u396608776/domains/uno14.trading/public_html/portalcolaborador/frontend.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    logger.debug("=== Starting Frontend WSGI ===")
    
    # Asegurar que el directorio del proyecto está en el path
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger.debug(f"Project directory: {project_dir}")
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    
    # Configurar variables de entorno
    os.environ['FLASK_APP'] = 'frontend_service'
    os.environ['FLASK_ENV'] = 'production'
    
    # Importar y crear la aplicación
    logger.debug("Creating Flask application...")
    from frontend_service import create_app
    app = create_app()
    logger.debug("Flask application created successfully")
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=8001)

except Exception as e:
    logger.error(f"Error in frontend wsgi.py: {str(e)}")
    logger.error(f"Python path: {sys.path}")
    raise 