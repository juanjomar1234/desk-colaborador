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

    from flask import Flask, session, redirect
    app = Flask(__name__)
    app.secret_key = 'your-secret-key-here'  # Necesario para session

    @app.route('/')
    def index():
        if 'token' not in session:
            return redirect('https://portalcolaborador.uno14.trading/auth/login')
        return "Logged in!"

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