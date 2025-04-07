#!/usr/bin/env python3
import os
import sys

# Añadir el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(__file__))

# Configurar variables de entorno para Flask
os.environ['FLASK_APP'] = 'frontend_service.app'
os.environ['FLASK_ENV'] = 'production'

from frontend_service.app import app
from wsgiref.handlers import CGIHandler

if __name__ == "__main__":
    print("Content-Type: text/html\n")
    CGIHandler().run(app) 