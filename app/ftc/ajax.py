from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from ftc.auth import login_required, admin_required
from ftc.db import get_db

from ftc.auth import login_required, admin_required
from ftc.db import get_db

bp = Blueprint('ajax', __name__)

@login_required
@admin_required
@bp.route('/ajax/_get_players_from_matchid')
def get_players_from_matchid():
    db = get_db()
    matchID = request.args.get('matchId', 0, type=int)
    isHomeTeam = request.args.get('isHomeTeam', 0, type=int)
    if isHomeTeam:
        res = db.execute('SELECT players.ID, players.short_name FROM season JOIN team_player ON team_player.teamID=season.HomeTeamID JOIN players ON players.ID=team_player.playerID WHERE matchID=?',(matchID,)).fetchall()
    else:
        res = db.execute('SELECT players.ID, players.short_name FROM season JOIN team_player ON team_player.teamID=season.AwayTeamID JOIN players ON players.ID=team_player.playerID WHERE matchID=?',(matchID,)).fetchall()
    players = []
    for row in res:
        players.append([x for x in row])
    return jsonify(players=players)


@login_required
@admin_required
@bp.route('/ajax/_get_players_from_query')
def get_player_from_query():
    def dict_from_row(row):
        return dict(zip(row.keys(), row))
    
    db = get_db()
    searchInput = request.args.get('searchInput', '', type=str)
    searchInput ="%"+searchInput+"%"
    res = db.execute('SELECT players.ID, players.short_name, players.club_name FROM players WHERE players.short_name LIKE ? OR players.club_name LIKE ?',(searchInput, searchInput)).fetchall()
    
    matching_players = []
    for row in res:
        matching_players.append(dict_from_row(row))

    return jsonify(matching_players)