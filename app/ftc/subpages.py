from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import BadRequestKeyError, abort

from ftc.auth import login_required, admin_required
from ftc.db import get_db

bp = Blueprint('subpages', __name__)

@bp.route('/matchreport', methods=['GET'])
@login_required
def matchReport():
    matchID = request.args.get('matchID')
    db = get_db()
    error = None
    if db.execute("SELECT matchID FROM season WHERE matchID=?",(matchID,)).fetchall() == []:
        error = "No Matchreport available for this Match"
        flash(error)
        return redirect(url_for('dashboard.schedule'))

    homeTeam = db.execute("SELECT gamer.TeamName FROM season JOIN gamer on gamer.ID=season.HomeTeamID WHERE season.MatchID=?",(matchID,)).fetchone()[0]
    awayTeam = db.execute("SELECT gamer.TeamName FROM season JOIN gamer on gamer.ID=season.AwayTeamID WHERE season.MatchID=?",(matchID,)).fetchone()[0]
    homeGoals = db.execute("SELECT season.HomeGoals FROM season WHERE season.MatchID=?",(matchID,)).fetchone()[0]
    awayGoals = db.execute("SELECT season.AwayGoals FROM season WHERE season.MatchID=?",(matchID,)).fetchone()[0]
    goals = db.execute(
                    """SELECT events.Minute, players.short_name, players.ID, goals.was_Penalty, goals.was_Owngoal, gamer.TeamName
                    FROM events
                    JOIN goals ON goals.ID = events.eventID
                    JOIN players On players.ID = goals.Scorer_ID
                    JOIN team_player ON team_player.playerID=players.ID
                    JOIN gamer ON gamer.ID=team_player.teamID
                    WHERE events.MatchID=? AND events.eventCategoryID=1
                    ORDER BY events.Minute ASC""", (matchID,)
                ).fetchall()
    cards = db.execute(
                    """SELECT events.Minute, players.short_name, players.ID, cards.cardCategory, gamer.TeamName
                    FROM events
                    JOIN cards ON cards.ID = events.eventID
                    JOIN players On players.ID = cards.ReceivingPlayer
                    JOIN team_player ON team_player.playerID=players.ID
                    JOIN gamer ON gamer.ID=team_player.teamID
                    WHERE events.MatchID=? AND events.eventCategoryID=2
                    ORDER BY events.Minute ASC""",(matchID,)
                ).fetchall()
    return render_template('subpages/matchreport.html', homeTeam=homeTeam, awayTeam=awayTeam, homeGoals=homeGoals, awayGoals=awayGoals, goals=goals, cards=cards)