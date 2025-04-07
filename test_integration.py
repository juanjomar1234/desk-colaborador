import requests
import json

def test_auth_service():
    """Prueba el servicio de autenticación"""
    base_url = "http://localhost:5000"
    
    # Prueba de registro
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        register_response = requests.post(
            f"{base_url}/api/auth/register",
            json=register_data
        )
        print(f"Registro: {register_response.status_code}")
        print(register_response.json())
    except Exception as e:
        print(f"Error en registro: {str(e)}")
    
    # Prueba de login
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data
        )
        print(f"Login: {login_response.status_code}")
        login_result = login_response.json()
        print(login_result)
        
        if "access_token" in login_result:
            token = login_result["access_token"]
            
            # Prueba de obtener información del usuario
            headers = {"Authorization": f"Bearer {token}"}
            user_response = requests.get(
                f"{base_url}/api/auth/user",
                headers=headers
            )
            print(f"Obtener usuario: {user_response.status_code}")
            print(user_response.json())
    except Exception as e:
        print(f"Error en login: {str(e)}")

def test_frontend_service():
    """Prueba el servicio frontend"""
    base_url = "http://localhost:5001"
    
    try:
        # Prueba de acceso a la página principal
        index_response = requests.get(base_url)
        print(f"Página principal: {index_response.status_code}")
        
        # Prueba de acceso a la página de login
        login_response = requests.get(f"{base_url}/login")
        print(f"Página de login: {login_response.status_code}")
    except Exception as e:
        print(f"Error en frontend: {str(e)}")

def test_integration():
    """Prueba la integración entre servicios"""
    auth_url = "http://localhost:5000"
    frontend_url = "http://localhost:5001"
    
    # Obtener token desde auth-service
    login_data = {
        "username": "admin",  # Usuario por defecto
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            f"{auth_url}/api/auth/login",
            json=login_data
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            
            # Verificar token en frontend-service
            check_auth_response = requests.get(
                f"{frontend_url}/check-auth",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"Verificación de token: {check_auth_response.status_code}")
            print(check_auth_response.json())
    except Exception as e:
        print(f"Error en integración: {str(e)}")

if __name__ == "__main__":
    print("=== Pruebas del Servicio de Autenticación ===")
    test_auth_service()
    
    print("\n=== Pruebas del Servicio Frontend ===")
    test_frontend_service()
    
    print("\n=== Pruebas de Integración ===")
    test_integration()
