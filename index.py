#!/usr/bin/env python3

from frontend_service.app import app

if __name__ == "__main__":
    print("Content-Type: text/html\n")  # Necesario para CGI
    app.run(host='0.0.0.0', port=5000) 