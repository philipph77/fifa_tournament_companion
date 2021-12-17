import pytest
from flask import g, session
from ftc.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'firstname': 'Vax', 'lastname': 'Merstappen', 'username': 'a', 'teamname': 'Bed Rull', 'password': 'a', 'tournament_key': 'BangerCup0707!'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM gamer WHERE username = 'johndoe77'",
        ).fetchone() is not None


@pytest.mark.parametrize(('firstname', 'lastname', 'username', 'teamname', 'password', 'tournament_key', 'message'), (
    # TODO: alle cases abdecken!
    ('', '', '', '', '', '', b'Firstname is required.'),
    ('Vax', '', '', '', '', '', b'Lastname is required.'),
    ('Vax', 'Merstappen', '', '', '', '', b'Username is required.'),
    ('Vax', 'Merstappen', 'max33', '', '', '', b'Teamname is required.'),
    ('Vax', 'Merstappen', 'max33', 'Bed Rull', '', '', b'Password is required.'),
    ('Vax', 'Merstappen', 'max33', 'Bed Rull', 'test', '', b"Wrong Tournament key. If you dont have the tournament key, ask your tournament admin"),
    #('Vax', 'Merstappen', 'max33', 'Bed Rull', 'test', 'BangerCup0707!', b'Something went wrong. Either the username max33 or the teamname Bed Rull is already registered. Try to choose another one. If the error keeps occuring, please contact the admin.')
))


def test_register_validate_input(client, firstname, lastname, username, teamname, password, tournament_key, message):
    response = client.post(
        '/auth/register',
        data={
            'firstname': firstname,
            'lastname':lastname,
            'username': username,
            'teamname':teamname,
            'password': password,
            'tournament_key': tournament_key
            }
    )
    assert message in response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'johndoe77'



@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'There is no user with this username.'),
    ('johndoe77', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session