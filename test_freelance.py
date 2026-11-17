import pytest

from freelance_service import create_app
from freelance_service.models import db


@pytest.fixture
def app(tmp_path):
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f"sqlite:///{tmp_path / 'test.db'}",
    })
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


PROJECT = {'title': 'MVP', 'description': 'Portal', 'skills': 'Python, Flask, SQL',
           'budget_max': 5000, 'deadline': '2030-01-31'}


def proposal(email='a@example.com', **extra):
    data = {'name': 'Ana', 'email': email, 'skills': 'python, flask',
            'amount': 4000, 'days': 30, 'message': 'Hola'}
    data.update(extra)
    return data


def make_project(client, **extra):
    res = client.post('/api/projects', json={**PROJECT, **extra})
    assert res.status_code == 201
    return res.get_json()


def test_health(client):
    assert client.get('/health').get_json()['status'] == 'ok'


def test_create_project_normalizes_skills(client):
    project = make_project(client)
    assert project['skills'] == ['python', 'flask', 'sql']
    assert project['status'] == 'abierto'
    assert client.get('/api/projects').get_json()[0]['id'] == project['id']


@pytest.mark.parametrize('payload,error', [
    ({'description': 'x', 'budget_max': 10}, 'title'),
    ({'title': 'x', 'description': 'x', 'budget_max': 'abc'}, 'numérico'),
    ({'title': 'x', 'description': 'x', 'budget_min': 50, 'budget_max': 10}, 'mínimo'),
    ({'title': 'x', 'description': 'x', 'budget_max': 10, 'deadline': '31/01'}, 'AAAA'),
])
def test_create_project_validation(client, payload, error):
    res = client.post('/api/projects', json=payload)
    assert res.status_code == 400
    assert error in res.get_json()['error']


def test_submit_and_rank_proposals(client):
    pid = make_project(client)['id']
    client.post(f'/api/projects/{pid}/proposals', json=proposal('low@example.com', skills='php'))
    res = client.post(f'/api/projects/{pid}/proposals',
                      json=proposal('top@example.com', skills='python, flask, sql', amount=6000))
    assert res.status_code == 201
    body = res.get_json()
    assert body['skill_match'] == 100
    assert body['within_budget'] is False
    ranked = client.get(f'/api/projects/{pid}/proposals').get_json()
    assert [p['freelancer']['email'] for p in ranked] == ['top@example.com', 'low@example.com']
    assert len(client.get('/api/freelancers').get_json()) == 2


def test_duplicate_proposal_rejected(client):
    pid = make_project(client)['id']
    assert client.post(f'/api/projects/{pid}/proposals', json=proposal()).status_code == 201
    res = client.post(f'/api/projects/{pid}/proposals', json=proposal(email='A@example.com'))
    assert res.status_code == 409


def test_shortlist_and_hire_flow(client):
    pid = make_project(client)['id']
    first = client.post(f'/api/projects/{pid}/proposals', json=proposal('a@example.com')).get_json()
    second = client.post(f'/api/projects/{pid}/proposals', json=proposal('b@example.com')).get_json()

    res = client.patch(f"/api/proposals/{first['id']}", json={'status': 'preseleccionada'})
    assert res.get_json()['status'] == 'preseleccionada'
    assert client.patch(f"/api/proposals/{first['id']}", json={'status': 'aceptada'}).status_code == 400

    res = client.post(f"/api/proposals/{first['id']}/hire")
    assert res.status_code == 201
    contract = res.get_json()
    assert contract['amount'] == 4000 and contract['status'] == 'activo'

    project = client.get(f'/api/projects/{pid}').get_json()
    assert project['status'] == 'contratado'
    statuses = {p['id']: p['status'] for p in project['proposals']}
    assert statuses == {first['id']: 'aceptada', second['id']: 'rechazada'}

    assert client.post(f"/api/proposals/{second['id']}/hire").status_code == 409
    assert client.post(f'/api/projects/{pid}/proposals', json=proposal('c@example.com')).status_code == 409

    res = client.post(f"/api/contracts/{contract['id']}/complete")
    assert res.get_json()['status'] == 'finalizado'
    assert client.get(f'/api/projects/{pid}').get_json()['status'] == 'cerrado'
    stats = client.get('/api/stats').get_json()
    assert stats['active_contracts'] == 0 and stats['committed_budget'] == 4000


def test_close_project_rejects_open_proposals(client):
    pid = make_project(client)['id']
    prop = client.post(f'/api/projects/{pid}/proposals', json=proposal()).get_json()
    assert client.post(f'/api/projects/{pid}/close').get_json()['status'] == 'cerrado'
    assert client.get(f'/api/projects/{pid}').get_json()['proposals'][0]['status'] == 'rechazada'
    assert client.post(f"/api/proposals/{prop['id']}/hire").status_code == 409


def test_not_found(client):
    assert client.get('/api/projects/999').status_code == 404
    assert client.get('/projects/999').status_code == 404


def test_html_flow(client):
    res = client.post('/projects/new', data={**PROJECT, 'budget_max': '5000'})
    assert res.status_code == 302
    detail_url = res.headers['Location']
    pid = int(detail_url.rstrip('/').split('/')[-1])

    res = client.post(f'/projects/{pid}/apply', data={k: str(v) for k, v in proposal().items()})
    assert 'Propuesta enviada' in res.get_data(as_text=True)

    page = client.get(detail_url).get_data(as_text=True)
    assert 'Ana' in page and 'Contratar' in page

    res = client.post('/proposals/1/hire', follow_redirects=True)
    assert 'contratado/a' in res.get_data(as_text=True)
    assert 'Ana' in client.get('/contracts').get_data(as_text=True)
    for path in ('/', '/freelancers', '/projects/new'):
        assert client.get(path).status_code == 200


def test_html_validation_error_is_shown(client):
    res = client.post('/projects/new', data={'title': '', 'description': '', 'budget_max': ''})
    assert res.status_code == 200
    assert 'obligatorio' in res.get_data(as_text=True)


def test_seed_demo_command(app):
    result = app.test_cli_runner().invoke(args=['seed-demo'])
    assert 'cargados' in result.output
    with app.app_context():
        from freelance_service.models import Proposal
        assert Proposal.query.count() == 4


@pytest.mark.parametrize('value', ['nan', 'inf', '-inf'])
def test_non_finite_amounts_rejected(client, value):
    assert client.post('/api/projects', json={**PROJECT, 'budget_max': value}).status_code == 400
    pid = make_project(client)['id']
    res = client.post(f'/api/projects/{pid}/proposals', json=proposal(amount=value))
    assert res.status_code == 400


def test_portfolio_url_must_be_http(client):
    pid = make_project(client)['id']
    res = client.post(f'/api/projects/{pid}/proposals',
                      json=proposal(portfolio_url='javascript:alert(1)'))
    assert res.status_code == 400
    res = client.post(f'/api/projects/{pid}/proposals',
                      json=proposal(portfolio_url='https://example.com/ana'))
    assert res.status_code == 201


def test_existing_profile_not_overwritten(client):
    first = make_project(client)['id']
    second = make_project(client, title='Otro')['id']
    client.post(f'/api/projects/{first}/proposals', json=proposal())
    res = client.post(f'/api/projects/{second}/proposals',
                      json=proposal(name='Impostor', skills='hacking'))
    assert res.status_code == 201
    freelancer = client.get('/api/freelancers').get_json()[0]
    assert freelancer['name'] == 'Ana' and freelancer['skills'] == ['python', 'flask']


def test_cannot_close_hired_project(client):
    pid = make_project(client)['id']
    prop = client.post(f'/api/projects/{pid}/proposals', json=proposal()).get_json()
    client.post(f"/api/proposals/{prop['id']}/hire")
    assert client.post(f'/api/projects/{pid}/close').status_code == 409
    assert client.get('/api/contracts').get_json()[0]['status'] == 'activo'


def test_hire_confirm_does_not_embed_user_data(client):
    pid = make_project(client)['id']
    client.post(f'/api/projects/{pid}/proposals', json=proposal(name="x');alert(1);//"))
    page = client.get(f'/projects/{pid}').get_data(as_text=True)
    assert 'alert(1)' not in page.split('onsubmit')[-1].split('>')[0]
    assert "confirm('¿Contratar esta propuesta?" in page
