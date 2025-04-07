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
    # Añadir el directorio actual al path de Python
    sys.path.insert(0, os.path.dirname(__file__))
    logging.info(f"Python path: {sys.path}")

    # Configurar variables de entorno para Flask
    os.environ['FLASK_APP'] = 'frontend_service.app'
    os.environ['FLASK_ENV'] = 'production'

    from frontend_service.app import app
    from wsgiref.handlers import CGIHandler

    if __name__ == "__main__":
        print("Content-Type: text/html\n")
        CGIHandler().run(app)

except Exception as e:
    logging.error(f"Error: {str(e)}")
    logging.error(f"Traceback: {traceback.format_exc()}")
    print("Content-Type: text/html\n")
    print("<h1>Internal Server Error</h1>")
    print("<pre>")
    print(traceback.format_exc())
    print("</pre>") 