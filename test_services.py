import unittest
import json
from unittest.mock import patch

class TestAuthService(unittest.TestCase):
    """Pruebas unitarias para el servicio de autenticación"""
    
    @classmethod
    def setUpClass(cls):
        from auth_service import create_app
        cls.app = create_app({'TESTING': True})
        cls.client = cls.app.test_client()
        cls.ctx = cls.app.app_context()
        cls.ctx.push()  # Push the context

    @classmethod
    def tearDownClass(cls):
        cls.ctx.pop()  # Remove the context when done

    def setUp(self):
        with self.app.app_context():
            from auth_service import db
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            from auth_service import db
            db.session.remove()
            db.drop_all()

    def test_login_endpoint(self):
        """Prueba el endpoint de login con credenciales correctas"""
        response = self.client.post('/auth/login', 
            json={'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 200)
    
    def test_login_invalid_credentials(self):
        """Prueba el endpoint de login con credenciales incorrectas"""
        response = self.client.post('/auth/login',
            json={'username': 'admin', 'password': 'wrong_password'})
        self.assertEqual(response.status_code, 401)
    
    def test_register_endpoint(self):
        """Prueba el endpoint de registro"""
        import random
        username = f"testuser_{random.randint(1000, 9999)}"
        
        response = self.client.post('/auth/register',
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "password123"
            })
        self.assertIn(response.status_code, [201, 409])
    
    def test_protected_endpoint(self):
        """Prueba un endpoint protegido con y sin token"""
        # Sin token
        response = self.client.get('/auth/user')
        self.assertIn(response.status_code, [401, 422])
        
        # Con token
        login_response = self.client.post('/auth/login',
            json={'username': 'test', 'password': 'test'})
        
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json.get("access_token")
        self.assertIsNotNone(token)
        
        response = self.client.get('/auth/user',
            headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)

class TestFrontendService(unittest.TestCase):
    """Pruebas unitarias para el servicio frontend"""
    
    @classmethod
    def setUpClass(cls):
        from frontend_service import create_app
        cls.app = create_app({'TESTING': True})
        cls.client = cls.app.test_client()

    def test_index_page(self):
        """Prueba el acceso a la página principal"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        """Prueba el acceso a la página de login"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
    
    def test_check_auth_endpoint(self):
        """Prueba el endpoint de verificación de autenticación"""
        # Sin token
        response = self.client.get('/check-auth')
        self.assertEqual(response.status_code, 401)
        
        # Con token válido (mock del auth service)
        with patch('frontend_service.middleware.auth.requests.get') as mock_auth:
            mock_auth.return_value.status_code = 200
            mock_auth.return_value.json.return_value = {"valid": True}
            
            response = self.client.get('/check-auth',
                headers={"Authorization": "Bearer test_token"})
            self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
