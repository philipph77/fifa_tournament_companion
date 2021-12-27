import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def load_players(year):
    db = get_db()
    with current_app.open_resource(f"players{year}.sql") as f:
        db.executescript(f.read().decode('utf8'))

def make_admin(id):
    db = get_db()
    db.execute("UPDATE user SET isAdmin=1 WHERE ID=?",(id,))
    db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

@click.command('load-players')
@click.argument('year')
@with_appcontext
def load_players_command(year):
    """Load the FIFA players."""
    try:
        load_players(year)
        click.echo(f'FIFA{year} Players loaded.')
    except FileNotFoundError:
        click.echo('Error: Players not available. Try another year, e.g. 21 or 22')

@click.command('make-admin')
@click.argument('id')
@with_appcontext
def make_admin_command(id):
    """Make a user an admin."""
    make_admin(id)
    click.echo(f'User {id} is now an admin.')    

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(load_players_command)
    app.cli.add_command(make_admin_command)