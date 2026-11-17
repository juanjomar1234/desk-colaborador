import unittest
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class TestCreateUserAPI(unittest.TestCase):
    """Pruebas del endpoint POST /api/users/"""

    def setUp(self):
        from auth_service import create_app, db
        from auth_service.models.user import User
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            user = User(username='pepe', email='pepe@example.com', role='user')
            user.set_password('pepe123')
            db.session.add_all([admin, user])
            db.session.commit()

    def _token(self, username, password):
        response = self.client.post('/login', json={'username': username, 'password': password})
        self.assertEqual(response.status_code, 200)
        return {'Authorization': f"Bearer {response.json['access_token']}"}

    def _post(self, payload, headers=None):
        return self.client.post('/api/users/', json=payload, headers=headers or {})

    def test_admin_creates_user(self):
        headers = self._token('admin', 'admin123')
        response = self._post({'username': 'ana', 'email': 'ana@example.com',
                               'password': 'secreto', 'role': 'admin'}, headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['user']['username'], 'ana')
        self.assertEqual(response.json['user']['role'], 'admin')
        self.assertNotIn('password_hash', response.json['user'])
        self.assertEqual(self.client.post('/login', json={
            'username': 'ana', 'password': 'secreto'}).status_code, 200)

    def test_default_role_is_user(self):
        headers = self._token('admin', 'admin123')
        response = self._post({'username': 'luis', 'email': 'luis@example.com',
                               'password': 'secreto'}, headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['user']['role'], 'user')

    def test_requires_token(self):
        response = self._post({'username': 'x', 'email': 'x@example.com', 'password': 'x'})
        self.assertEqual(response.status_code, 401)

    def test_non_admin_forbidden(self):
        for headers in (self._token('pepe', 'pepe123'), self._token('test', 'test')):
            response = self._post({'username': 'x', 'email': 'x@example.com',
                                   'password': 'x'}, headers)
            self.assertEqual(response.status_code, 403)

    def test_test_login_does_not_inherit_admin_named_test(self):
        from auth_service import db
        from auth_service.models.user import User
        with self.app.app_context():
            admin = User(username='test', email='test@example.com', role='admin')
            admin.set_password('otra-clave')
            db.session.add(admin)
            db.session.commit()
        response = self._post({'username': 'x', 'email': 'x@example.com',
                               'password': 'x', 'role': 'admin'}, self._token('test', 'test'))
        self.assertEqual(response.status_code, 403)

    def test_validation_errors(self):
        headers = self._token('admin', 'admin123')
        response = self._post({'username': 'x'}, headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json['fields']), {'email', 'password'})
        self.assertEqual(self._post({'username': 'x', 'email': 'no-email',
                                     'password': 'x'}, headers).status_code, 400)
        self.assertEqual(self._post({'username': 'x', 'email': 'x@example.com',
                                     'password': 'x', 'role': 'superuser'}, headers).status_code, 400)
        self.assertEqual(self.client.post('/api/users/', data='no-json', headers=headers,
                                          content_type='text/plain').status_code, 400)

    def test_duplicates_conflict(self):
        headers = self._token('admin', 'admin123')
        self.assertEqual(self._post({'username': 'pepe', 'email': 'otro@example.com',
                                     'password': 'x'}, headers).status_code, 409)
        self.assertEqual(self._post({'username': 'otro', 'email': 'pepe@example.com',
                                     'password': 'x'}, headers).status_code, 409)

    def test_register_cannot_self_assign_admin(self):
        response = self.client.post('/register', json={
            'username': 'hacker', 'email': 'hacker@example.com',
            'password': 'x', 'role': 'admin'})
        self.assertEqual(response.status_code, 201)
        headers = self._token('hacker', 'x')
        self.assertEqual(self._post({'username': 'y', 'email': 'y@example.com',
                                     'password': 'y'}, headers).status_code, 403)


if __name__ == '__main__':
    unittest.main()
