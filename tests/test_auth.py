import pytest
from bookshelf_app.models import User


def test_registration(client):
    response = client.post('/api/v1/auth/register',
                           json={
                               'username': 'Test',
                               'password': '123456',
                               'email': 'test123@test.pl'
                           })
    data = response.get_json()
    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    assert data['success'] is True
    assert data['token']
    assert User.query.get(1).username == 'Test'


@pytest.mark.parametrize(
    'data, missing_field',
    [
        ({'username': 'Test', 'password': '123456'}, 'email'),
        ({'username': 'Test', 'email': 'test123@test.pl'}, 'password'),
        ({'password': '123456', 'email': 'test123@test.pl'}, 'username'),

    ])
def test_registration_wrong_data(client, data, missing_field):
    response = client.post('/api/v1/auth/register', json=data)
    response_data = response.get_json()
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert missing_field in response_data['message']
    assert 'Missing data for required field.' in response_data['message'][missing_field]


def test_registration_wrong_content_type(client):
    response = client.post('/api/v1/auth/register',
                           data={
                               'username': 'Test',
                               'password': '123456',
                               'email': 'test123@test.pl'
                           })
    response_data = response.get_json()
    assert response.status_code == 415
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data

def test_registration_username_used(client, user):
    response = client.post('/api/v1/auth/register',
                           json={
                               'username': user['username'],
                               'password': '123456',
                               'email': 'test@test.pl'
                           })
    response_data = response.get_json()
    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data


def test_registration_email_used(client, user):
    response = client.post('/api/v1/auth/register',
                           json={
                               'username': 'test123',
                               'password': '123456',
                               'email': user['email']
                           })
    response_data = response.get_json()
    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data

def test_get_curretn_user(client,user, token):
    response = client.get('/api/v1/auth/user',
                           headers={
                              'Authorization': f'Bearer {token}'
                           })
    data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert data['success'] is True
    assert data['data']['username'] == user['username']
    assert 'id' in data['data']
    assert 'creation_date' in data['data']

def test_get_curretn_user_no_token(client):
    response = client.get('/api/v1/auth/user')
    data = response.get_json()
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert data['success'] is False
    assert 'data' not in data