import unittest
import warnings

warnings.filterwarnings("ignore")


class TestApplicationsAPI(unittest.TestCase):
    """Pruebas para el endpoint /api/applications del servicio de autenticación"""

    def setUp(self):
        from auth_service import create_app, db
        from auth_service.models.user import User

        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            for username, role in (('admin', 'admin'), ('alice', 'user')):
                user = User(username=username, email=f'{username}@example.com', role=role)
                user.set_password('secret')
                db.session.add(user)
            db.session.commit()

        self.admin = self._auth_headers('admin')
        self.user = self._auth_headers('alice')

    def tearDown(self):
        from auth_service import db
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _auth_headers(self, username):
        response = self.client.post('/login', json={'username': username, 'password': 'secret'})
        self.assertEqual(response.status_code, 200)
        return {'Authorization': f"Bearer {response.json['access_token']}"}

    def test_requires_token(self):
        response = self.client.get('/api/applications/')
        self.assertEqual(response.status_code, 401)

    def test_list_returns_seeded_applications(self):
        response = self.client.get('/api/applications/', headers=self.user)
        self.assertEqual(response.status_code, 200)
        names = [a['name'] for a in response.json['applications']]
        self.assertEqual(len(names), 6)
        self.assertIn('Dashboard', names)

    def test_get_application(self):
        response = self.client.get('/api/applications/1', headers=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Auth Service')

        response = self.client.get('/api/applications/999', headers=self.user)
        self.assertEqual(response.status_code, 404)

    def test_non_admin_cannot_modify(self):
        self.assertEqual(self.client.post('/api/applications/', json={'name': 'X'},
                                          headers=self.user).status_code, 403)
        self.assertEqual(self.client.put('/api/applications/1', json={'name': 'X'},
                                         headers=self.user).status_code, 403)
        self.assertEqual(self.client.delete('/api/applications/1',
                                            headers=self.user).status_code, 403)

    def test_admin_crud(self):
        response = self.client.post('/api/applications/', headers=self.admin, json={
            'name': 'Wiki', 'description': 'Base de conocimiento', 'icon': 'book',
            'url': 'https://wiki.example.com'
        })
        self.assertEqual(response.status_code, 201)
        app_id = response.json['application']['id']
        self.assertTrue(response.json['application']['active'])

        response = self.client.put(f'/api/applications/{app_id}', headers=self.admin,
                                   json={'description': 'Docs', 'active': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['application']['description'], 'Docs')

        # Las aplicaciones inactivas se ocultan a usuarios normales
        names = [a['name'] for a in self.client.get('/api/applications/', headers=self.user).json['applications']]
        self.assertNotIn('Wiki', names)
        self.assertEqual(self.client.get(f'/api/applications/{app_id}', headers=self.user).status_code, 404)

        # ...pero el admin puede verlas con ?all=true
        names = [a['name'] for a in self.client.get('/api/applications/?all=true',
                                                    headers=self.admin).json['applications']]
        self.assertIn('Wiki', names)

        response = self.client.delete(f'/api/applications/{app_id}', headers=self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(f'/api/applications/{app_id}', headers=self.admin).status_code, 404)

    def test_validation_and_duplicates(self):
        self.assertEqual(self.client.post('/api/applications/', json={},
                                          headers=self.admin).status_code, 400)
        self.assertEqual(self.client.post('/api/applications/', json={'name': 'X', 'active': 'yes'},
                                          headers=self.admin).status_code, 400)
        self.assertEqual(self.client.post('/api/applications/', json={'name': 'Dashboard'},
                                          headers=self.admin).status_code, 409)
        self.assertEqual(self.client.put('/api/applications/1', json={'name': 'Dashboard'},
                                         headers=self.admin).status_code, 409)


if __name__ == '__main__':
    unittest.main()
