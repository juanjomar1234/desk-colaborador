import os
import sys

# Añadir el directorio actual al path de Python
INTERP = os.path.expanduser("/home/u396608776/domains/uno14.trading/public_html/portalcolaborador/venv/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Configurar paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación
from frontend_service.wsgi import app as application 