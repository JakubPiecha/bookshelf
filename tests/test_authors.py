import pytest


def test_get_authors_no_data(client):
    response = client.get('/api/v1/authors')
    result = {
        'success': True,
        'data': [],
        'number of records': 0,
        'pagination': {
            'total_pages': 0,
            'total_records': 0,
            'current_page': '/api/v1/authors?page=1',
        }
    }
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.get_json() == result


def test_get_authors(client, sample_data):
    response = client.get('/api/v1/authors')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['number of records'] == 5
    assert len(response_data['data']) == 5
    assert response_data['pagination'] == {
        'total_pages': 2,
        'total_records': 10,
        'current_page': '/api/v1/authors?page=1',
        'next_page': '/api/v1/authors?page=2',
    }


def test_get_authors_with_params(client, sample_data):
    response = client.get('/api/v1/authors?fields=first_name&sort=-id&page=2&limit=2')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['number of records'] == 2
    assert response_data['pagination'] == {
        'total_pages': 5,
        'total_records': 10,
        'current_page': '/api/v1/authors?page=2&fields=first_name&sort=-id&limit=2',
        'next_page': '/api/v1/authors?page=3&fields=first_name&sort=-id&limit=2',
        'prev_page': '/api/v1/authors?page=1&fields=first_name&sort=-id&limit=2'
    }
    assert response_data['data'] == [
        {
            'first_name': 'Alice'
        },
        {
            'first_name': 'Dan'
        }
    ]


def test_get_author(client, sample_data):
    response = client.get('/api/v1/authors/9')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['first_name'] == 'Andrzej'
    assert response_data['data']['last_name'] == 'Sapkowski'
    assert response_data['data']['birth_date'] == '21-06-1948'
    assert len(response_data['data']['books']) == 1


def test_get_author_not_exist(client, sample_data):
    response = client.get('/api/v1/authors/33')
    response_data = response.get_json()
    assert response.status_code == 404
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'data' not in response_data


def test_create_author(client, token, author):
    response = client.post('/api/v1/authors',
                           json=author,
                           headers={
                               'Authorization': f'Bearer {token}'
                           })
    response_data = response.get_json()
    expected = {
        'success': True,
        'data': {
            **author,
            'id': 1,
            'books': []
        }
    }
    assert response.status_code == 201
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data == expected

    response = client.get('/api/v1/authors/1')
    response_data = response.get_json()
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['data']['first_name'] == author['first_name']
    assert response_data['data']['last_name'] == author['last_name']
    assert response_data['data']['birth_date'] == author['birth_date']
    assert len(response_data['data']['books']) == 0


@pytest.mark.parametrize(
    'data, missing_field',
    [
        ({'last_name': 'Mickiewicz', 'first_name': 'Adam'}, 'birth_date'),
        ({'first_name': 'Adam', 'birth_date': '24-12-1788'}, 'last_name'),
        ({'last_name': 'Mickiewicz', 'birth_date': '24-12-1788'}, 'first_name'),

    ])
def test_add_author_wrong_data(client, token, data, missing_field):
    response = client.post('/api/v1/authors',
                           json=data,
                           headers={
                               'Authorization': f'Bearer {token}'
                           })
    response_data = response.get_json()
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'data' not in response_data
    assert missing_field in response_data['message']
    assert 'Missing data for required field.' in response_data['message'][missing_field]


def test_add_author_invalid_content_type(client, token, author):
    response = client.post('/api/v1/authors',
                           data=author,
                           headers={
                               'Authorization': f'Bearer {token}'
                           })
    response_data = response.get_json()
    assert response.status_code == 415
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'data' not in response_data


def test_add_author_no_token(client, author):
    response = client.post('/api/v1/authors',
                           json=author
                           )
    response_data = response.get_json()
    assert response.status_code == 401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'data' not in response_data
