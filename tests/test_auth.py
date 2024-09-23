import pytest # type: ignore
from flask import g, session # type: ignore
from flaskr.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a', 'confirmPassword': 'a'}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM users WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'confirmPassword', 'messages'), [
    ('', '', '', [b'errorArray.push(0)', b'errorArray.push(1)', b'errorArray.push(2)']),
    ('test', 'pass', 'pass', [b'errorArray.push(4)']),
    ('a', 'pass', 'passw', [b'errorArray.push(3)']),
    ('user', 'pass', 'pass', [])
])
def test_register_validate_input(client, username, password, confirmPassword, messages):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password, 'confirmPassword': confirmPassword}
    )

    for message in messages:
        print(message)
        assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'messages'), [
    ('', '', [b'errorArray.push(0)', b'errorArray.push(1)']),
    ('a', 'test', b'errorArray.push(5)'),
    ('test', 'a', b'errorArray.push(6)')
])
def test_login_validate_input(auth, username, password, messages):
    response = auth.login(username, password)

    for message in messages:
        assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session