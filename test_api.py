import unittest
import warnings

warnings.filterwarnings("ignore")


class TestAuthApi(unittest.TestCase):
    """Pruebas de la API REST del servicio de autenticación"""

    def setUp(self):
        from auth_service import create_app
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'JWT_SECRET_KEY': 'test-jwt-secret-key-with-32-bytes!!',
        })
        self.client = self.app.test_client()
        self._register('admin', 'admin123', role='admin')
        self._register('alice', 'alice123')

    def tearDown(self):
        from auth_service import db
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _register(self, username, password, role='user'):
        response = self.client.post('/register', json={
            'username': username,
            'email': f'{username}@example.com',
            'password': password,
            'role': role,
        })
        self.assertEqual(response.status_code, 201)

    def _auth(self, username, password):
        response = self.client.post('/login', json={'username': username, 'password': password})
        self.assertEqual(response.status_code, 200)
        return {'Authorization': f"Bearer {response.json['access_token']}"}

    def test_health(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'ok')
        self.assertEqual(response.json['database'], 'ok')

    def test_index_lists_api_endpoints(self):
        endpoints = self.client.get('/').json['endpoints']
        self.assertEqual(endpoints['health'], '/api/health')
        self.assertEqual(endpoints['me'], '/api/me')

    def test_me_requires_token(self):
        self.assertEqual(self.client.get('/api/me').status_code, 401)

    def test_me_returns_profile(self):
        response = self.client.get('/api/me', headers=self._auth('alice', 'alice123'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['username'], 'alice')
        self.assertEqual(response.json['role'], 'user')

    def test_me_unknown_user(self):
        response = self.client.get('/api/me', headers=self._auth('test', 'test'))
        self.assertEqual(response.status_code, 404)

    def test_test_login_does_not_inherit_real_test_account(self):
        self._register('test', 'other-password', role='admin')
        headers = self._auth('test', 'test')
        self.assertEqual(self.client.get('/api/me', headers=headers).status_code, 404)
        self.assertEqual(self.client.get('/api/users/', headers=headers).status_code, 403)

    def test_reused_username_does_not_transfer_access(self):
        alice_headers = self._auth('alice', 'alice123')
        alice_id = self.client.get('/api/me', headers=alice_headers).json['id']
        admin_headers = self._auth('admin', 'admin123')
        response = self.client.put(
            f'/api/users/{alice_id}', headers=admin_headers,
            json={'username': 'alice_old', 'email': 'alice_old@example.com'})
        self.assertEqual(response.status_code, 200)
        self._register('alice', 'new-alice-pass', role='admin')
        self.assertEqual(self.client.get('/api/me', headers=alice_headers).status_code, 404)
        self.assertEqual(self.client.get('/api/users/', headers=alice_headers).status_code, 403)

    def test_admin_lists_users(self):
        response = self.client.get('/api/users/', headers=self._auth('admin', 'admin123'))
        self.assertEqual(response.status_code, 200)
        usernames = {u['username'] for u in response.json['users']}
        self.assertEqual(usernames, {'admin', 'alice'})

    def test_non_admin_forbidden(self):
        headers = self._auth('alice', 'alice123')
        for url in ('/api/users/', '/api/roles/', '/api/permissions/'):
            self.assertEqual(self.client.get(url, headers=headers).status_code, 403, url)

    def test_user_can_read_own_profile(self):
        headers = self._auth('alice', 'alice123')
        me = self.client.get('/api/me', headers=headers).json
        response = self.client.get(f"/api/users/{me['id']}", headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_admin_lists_roles_and_permissions(self):
        headers = self._auth('admin', 'admin123')
        roles = self.client.get('/api/roles/', headers=headers)
        self.assertEqual(roles.status_code, 200)
        self.assertIn('admin', {r['name'] for r in roles.json['roles']})
        permissions = self.client.get('/api/permissions/', headers=headers)
        self.assertEqual(permissions.status_code, 200)
        self.assertGreater(len(permissions.json['permissions']), 0)


if __name__ == '__main__':
    unittest.main()
