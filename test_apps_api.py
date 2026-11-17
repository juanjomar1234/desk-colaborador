import unittest
import warnings

warnings.filterwarnings("ignore")


class TestAppsApi(unittest.TestCase):
    """Pruebas del catálogo de aplicaciones (/api/apps)"""

    def setUp(self):
        from auth_service import create_app
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'JWT_SECRET_KEY': 'test-jwt-secret-key-with-32-bytes!!',
        })
        self.client = self.app.test_client()
        self.admin = self._login('admin', 'admin123', role='admin')
        self.user = self._login('alice', 'alice123')

    def tearDown(self):
        from auth_service import db
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _login(self, username, password, role='user'):
        self.client.post('/register', json={
            'username': username,
            'email': f'{username}@example.com',
            'password': password,
            'role': role,
        })
        response = self.client.post('/login', json={'username': username, 'password': password})
        return {'Authorization': f"Bearer {response.json['access_token']}"}

    def _create(self, **data):
        return self.client.post('/api/apps/', json=data, headers=self.admin)

    def test_requires_token(self):
        self.assertEqual(self.client.get('/api/apps/').status_code, 401)

    def test_lists_default_apps(self):
        response = self.client.get('/api/apps/', headers=self.user)
        self.assertEqual(response.status_code, 200)
        names = [a['name'] for a in response.json['apps']]
        self.assertEqual(len(names), 6)
        self.assertIn('Dashboard', names)
        self.assertEqual(set(response.json['apps'][0]),
                         {'id', 'name', 'icon', 'description', 'url', 'enabled'})

    def test_admin_crud(self):
        created = self._create(name='Chat', icon='comments', url='/chat')
        self.assertEqual(created.status_code, 201)
        app_id = created.json['app']['id']
        self.assertTrue(created.json['app']['enabled'])

        updated = self.client.put(f'/api/apps/{app_id}', json={'description': 'Mensajería'},
                                  headers=self.admin)
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json['app']['description'], 'Mensajería')
        self.assertEqual(updated.json['app']['name'], 'Chat')

        fetched = self.client.get(f'/api/apps/{app_id}', headers=self.user)
        self.assertEqual(fetched.json['url'], '/chat')

        self.assertEqual(self.client.delete(f'/api/apps/{app_id}', headers=self.admin).status_code, 200)
        self.assertEqual(self.client.get(f'/api/apps/{app_id}', headers=self.admin).status_code, 404)

    def test_non_admin_cannot_modify(self):
        self.assertEqual(self.client.post('/api/apps/', json={'name': 'X'}, headers=self.user).status_code, 403)
        self.assertEqual(self.client.put('/api/apps/1', json={'name': 'X'}, headers=self.user).status_code, 403)
        self.assertEqual(self.client.delete('/api/apps/1', headers=self.user).status_code, 403)

    def test_validation_and_conflicts(self):
        self.assertEqual(self._create(icon='x').status_code, 400)
        self.assertEqual(self._create(name='Y', enabled='yes').status_code, 400)
        self.assertEqual(self._create(name='Dashboard').status_code, 409)
        self.assertEqual(self.client.put('/api/apps/1', json={'name': 'Dashboard'},
                                         headers=self.admin).status_code, 409)
        self.assertEqual(self.client.put('/api/apps/999', json={}, headers=self.admin).status_code, 404)

    def test_disabled_apps_hidden_from_users(self):
        app_id = self._create(name='Beta', enabled=False).json['app']['id']
        user_names = [a['name'] for a in self.client.get('/api/apps/', headers=self.user).json['apps']]
        self.assertNotIn('Beta', user_names)
        self.assertEqual(self.client.get(f'/api/apps/{app_id}', headers=self.user).status_code, 404)
        admin_all = self.client.get('/api/apps/?all=true', headers=self.admin).json['apps']
        self.assertIn('Beta', [a['name'] for a in admin_all])


if __name__ == '__main__':
    unittest.main()
