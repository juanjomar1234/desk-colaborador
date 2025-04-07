#!/usr/bin/env python3
import os
import sys
import logging
import traceback

# Configurar logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'app.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    # Añadir los directorios necesarios al path de Python
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'frontend_service'))
    sys.path.insert(0, os.path.join(current_dir, 'lib'))
    logging.info(f"Python path: {sys.path}")

    # Configurar variables de entorno para Flask
    os.environ['FLASK_APP'] = 'frontend-service'
    os.environ['FLASK_ENV'] = 'production'
    os.environ['AUTH_SERVICE_URL'] = 'https://portalcolaborador.uno14.trading/auth'

    from frontend_service import create_app
    from frontend_service.middleware.auth import require_auth

    app = create_app()
    app.before_request(require_auth)

    if __name__ == "__main__":
        print("Content-Type: text/html\n")
        from wsgiref.handlers import CGIHandler
        CGIHandler().run(app)

except Exception as e:
    logging.error(f"Error: {str(e)}")
    logging.error(f"Traceback: {traceback.format_exc()}")
    print("Content-Type: text/html\n")
    print("<h1>Internal Server Error</h1>")
    print("<pre>")
    print(traceback.format_exc())
    print("</pre>") 