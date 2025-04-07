import unittest
import requests

class TestAuthService(unittest.TestCase):
    """Pruebas unitarias para el servicio de autenticación"""
    
    BASE_URL = "http://localhost:5000"
    
    def test_login_endpoint(self):
        """Prueba el endpoint de login con credenciales correctas"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            json=login_data
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
    
    def test_login_invalid_credentials(self):
        """Prueba el endpoint de login con credenciales incorrectas"""
        login_data = {
            "username": "admin",
            "password": "wrong_password"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            json=login_data
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_register_endpoint(self):
        """Prueba el endpoint de registro"""
        # Generar un nombre de usuario único para evitar conflictos
        import random
        username = f"testuser_{random.randint(1000, 9999)}"
        
        register_data = {
            "username": username,
            "email": f"{username}@example.com",
            "password": "password123"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/auth/register",
            json=register_data
        )
        
        # Podría ser 201 (creado) o 409 (conflicto si ya existe)
        self.assertIn(response.status_code, [201, 409])
    
    def test_protected_endpoint(self):
        """Prueba un endpoint protegido con y sin token"""
        # Primero sin token
        response = requests.get(f"{self.BASE_URL}/api/auth/user")
        self.assertIn(response.status_code, [401, 422])  # Unauthorized o Unprocessable Entity
        
        # Ahora con token
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = requests.post(
            f"{self.BASE_URL}/api/auth/login",
            json=login_data
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            
            response = requests.get(
                f"{self.BASE_URL}/api/auth/user",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            self.assertEqual(response.status_code, 200)

class TestFrontendService(unittest.TestCase):
    """Pruebas unitarias para el servicio frontend"""
    
    BASE_URL = "http://localhost:5001"
    
    def test_index_page(self):
        """Prueba el acceso a la página principal"""
        response = requests.get(self.BASE_URL)
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        """Prueba el acceso a la página de login"""
        response = requests.get(f"{self.BASE_URL}/login")
        self.assertEqual(response.status_code, 200)
    
    def test_check_auth_endpoint(self):
        """Prueba el endpoint de verificación de autenticación"""
        # Sin token
        response = requests.get(f"{self.BASE_URL}/check-auth")
        self.assertEqual(response.status_code, 401)
        
        # Con token válido
        auth_url = "http://localhost:5000"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        login_response = requests.post(
            f"{auth_url}/api/auth/login",
            json=login_data
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            
            response = requests.get(
                f"{self.BASE_URL}/check-auth",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json().get("authenticated"))

if __name__ == "__main__":
    unittest.main()
