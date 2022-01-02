from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import BadRequestKeyError, abort

from ftc.auth import login_required, admin_required
from ftc.db import get_db

from ftc.helper import getMarketValueOfTeam
from ftc.helper import getStrengthOfTeam

bp = Blueprint('profile', __name__)

@bp.route('/profile')
@login_required
def profile():
    gamerID = request.args.get('gamerID')
    if gamerID == None:
        gamerID = g.gamer['ID']
    db = get_db()
    marketValue = getMarketValueOfTeam(db, gamerID)
    teamStrength = getStrengthOfTeam(db, gamerID)
    gamer = db.execute('SELECT FirstName, LastName, TeamName FROM gamer WHERE ID=?',(gamerID,)).fetchone()
    players = db.execute('SELECT players.short_name, players.overall, players.player_positions, players.ID FROM team_player JOIN players ON players.ID=team_player.playerID WHERE team_player.teamID=?',(gamerID,)).fetchall()
    
    return render_template('profile/profile.html', gamer=gamer, marketValue=marketValue, teamStrength=teamStrength, players=players)