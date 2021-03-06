from os import environ
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from ftc.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname'] 
        username = request.form['username']
        teamname = request.form['teamname']
        password = request.form['password']
        tournament_key = request.form['tournament_key']
        db = get_db()
        error = None

        if not firstname:
            error = 'Firstname is required.'
        elif not lastname:
            error = 'Lastname is required.'
        elif not username:
            error = 'Username is required.'
        elif not teamname:
            error = 'Teamname is required.'
        elif not password:
            error = 'Password is required.'
        elif not tournament_key == environ.get('TOURNAMENT_KEY'):
            error = "Wrong Tournament key. If you dont have the tournament key, ask your tournament admin"

        if error is None:
            try:
                userID = db.execute("INSERT INTO user (UserName, Password) VALUES (?,?) RETURNING ID",(username, generate_password_hash(password))).fetchone()[0]
                db.execute("INSERT INTO gamer(UserID, FirstName, LastName, TeamName) VALUES (?,?,?,?)",(userID, firstname, lastname, teamname))
                db.commit()
            except db.IntegrityError:
                error = f"Something went wrong. Either the username {username} or the teamname {teamname} is already registered. Try to choose another one. If the error keeps occuring, please contact the admin."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = f"There is no user with this username."
        elif not check_password_hash(user['Password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['ID']
            return redirect(url_for('index'))

        flash(error)
    else:
        session.clear()
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
        g.gamer = None
        g.isAdmin = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE ID = ?', (user_id,)).fetchone()
        g.gamer = get_db().execute('SELECT * FROM gamer WHERE UserID = ?', (user_id,)).fetchone()
        g.isAdmin = get_db().execute(
            'SELECT isAdmin FROM user WHERE ID = ?',(user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@bp.route('/403')
def forbidden():
    return render_template('auth/403.html')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not(g.isAdmin[0]==1):
            return redirect(url_for('auth.forbidden'))
        return view(**kwargs)

    return wrapped_view