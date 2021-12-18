from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import BadRequestKeyError, abort

from ftc.auth import login_required, admin_required
from ftc.db import get_db

from ftc.helper import calculateTables
from ftc.helper import calculateScorerStats
from ftc.helper import calculateCardStats
from ftc.helper import getWholeSchedule
from ftc.helper import getUpcomingGames
from ftc.helper import generateSchedule
from ftc.helper import getMarketValueOfTeam
from ftc.helper import getStrengthOfTeam
from ftc.helper import getNextGamesOfTeam
from ftc.helper import downloadPlayerImage

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    teamName = g.user[5]
    teamId = g.user[0]

    table, _, _ = calculateTables(db)
    tablePlace = table[table['Team']==teamName].index.values[0]
    points = table[table['Team']==teamName].Points.values[0]
    scoredGoals = table[table['Team']==teamName].Goals_For.values[0]
    receivedGoals = table[table['Team']==teamName].Goals_Against.values[0]

    marketValue = getMarketValueOfTeam(db, teamId)
    teamStrength = getStrengthOfTeam(db, teamId)

    nextGames = getNextGamesOfTeam(db, teamId)

    players = db.execute('SELECT players.short_name, players.overall, players.player_positions, players.ID FROM team_player JOIN players ON players.ID=team_player.playerID WHERE team_player.teamID=?',(teamId,)).fetchall()

    return render_template('dashboard/index.html', tablePlace=tablePlace, points=points, scoredGoals=scoredGoals, receivedGoals=receivedGoals, marketValue=marketValue, teamStrength=teamStrength, players=players, nextGames=nextGames)

@bp.route('/standings')
@login_required
def standings():
    db = get_db()
    table, homeTable, awayTable = calculateTables(db)
    scorerTable, assistTable, penaldoTable = calculateScorerStats(db)
    yellowCards, redCards = calculateCardStats(db)

    return render_template('dashboard/standings.html', table=table, homeTable=homeTable, awayTable=awayTable, scorerTable=scorerTable, assistTable=assistTable, penaldoTable=penaldoTable, yellowCards=yellowCards, redCards=redCards)

@bp.route('/schedule')
@login_required
def schedule():
    db = get_db()
    wholeSchedule = getWholeSchedule(db)
    upcomingGames = getUpcomingGames(db)
    return render_template('dashboard/schedule.html', wholeSchedule=wholeSchedule, upcomingGames=upcomingGames)

@bp.route('/admintools')
@login_required
@admin_required
def admintools():
    db = get_db()
    players = db.execute("SELECT ID, short_name, ifnull(club_name, 'N/A') FROM players").fetchall()
    gamers = db.execute('SELECT ID, FirstName, TeamName FROM gamer').fetchall()
    playersPerTeam = db.execute('SELECT team_player.playerID, players.short_name, gamer.FirstName, gamer.TeamName FROM team_player JOIN players ON players.ID=team_player.playerID JOIN gamer ON gamer.ID = team_player.teamID').fetchall()
    unfinishedMatches = db.execute("SELECT season.MatchID, season.MatchDay, gamer1.TeamName, gamer2.TeamName, gamer1.FirstName, gamer2.FirstName, season.HomeTeamID, season.AwayTeamID FROM season JOIN gamer gamer1 ON gamer1.ID = season.HomeTeamID JOIN gamer gamer2 ON gamer2.ID = season.AwayTeamID WHERE season.Is_Finished=0").fetchall()
    finishedMatches = db.execute("SELECT season.MatchID, season.MatchDay, gamer1.TeamName, gamer2.TeamName, gamer1.FirstName, gamer2.FirstName, season.HomeTeamID, season.AwayTeamID FROM season JOIN gamer gamer1 ON gamer1.ID = season.HomeTeamID JOIN gamer gamer2 ON gamer2.ID = season.AwayTeamID WHERE season.Is_Finished=1").fetchall()
    return render_template('dashboard/admintools.html', unfinishedMatches=unfinishedMatches, finishedMatches=finishedMatches, gamers=gamers, players=players, playersPerTeam=playersPerTeam)

@bp.route('/admintools/add-results', methods=('POST',))
@login_required
@admin_required
def add_results():
    
    db = get_db()

    if request.method == 'POST':
        matchID = int(request.form['matchID'])
        homeGoals = int(request.form['homeGoals'])
        awayGoals = int(request.form['awayGoals'])
        numberOfCards = int(request.form['cards'])
        cardsData = []
        for i in range(1, numberOfCards+1):
            cardsData.append( (int(request.form['cardPlayer-%i'%i]), int(request.form['cardMinute-%i'%i]), int(request.form['cardWasYellow-%i'%i])) )
        goalsData = []
        for i in range(1, homeGoals+1):
            try:
                request.form['wasPenalty-hg-%i'%i]
            except BadRequestKeyError:
                wasPenalty = 0
            else:
                wasPenalty = 1
            # check for owngoal
            if db.execute('SELECT team_player.playerID FROM team_player JOIN season ON season.HomeTeamID=team_player.teamID WHERE team_player.playerID=? AND season.MatchID=?',(int(request.form['homeGoalSelect-%i'%i]), matchID)).fetchone():
                wasOwnGoal = 0
            else:
                wasOwnGoal = 1
            goalsData.append( (int(request.form['homeGoalSelect-%i'%i]), int(request.form['homeGoalMinute-%i'%i]), wasPenalty, wasOwnGoal) )

        for i in range(1, awayGoals+1):
            try:
                request.form['wasPenalty-ag-%i'%i]
            except KeyError:
                wasPenalty = 0
            else:
                wasPenalty = 1
            # check for owngoal
            if db.execute('SELECT team_player.playerID FROM team_player JOIN season ON season.AwayTeamID=team_player.teamID WHERE team_player.playerID=? AND season.MatchID=?',(int(request.form['awayGoalSelect-%i'%i]), matchID)).fetchone():
                wasOwnGoal = 0
            else:
                wasOwnGoal = 1
            goalsData.append( (int(request.form['awayGoalSelect-%i'%i]), int(request.form['awayGoalMinute-%i'%i]), wasPenalty, wasOwnGoal) )

    error = None
    if not matchID:
        error = 'Select a Match'

    if error is not None:
        flash(error)
        return redirect(url_for('dashboard.admintools'))

    if homeGoals > awayGoals:
            matchResult = 1 # Heimsieg / home team won
    elif homeGoals == awayGoals:
        matchResult = 0 # Unentschieden / draw
    else:
        matchResult = 2 # Auswärtssieg / away team won


    for cardData in cardsData:
        cardId = db.execute('INSERT INTO events (MatchID, Minute, eventCategoryID) VALUES (?, ?, ?) RETURNING eventID',(matchID, cardData[1], 2)).fetchone()
        db.execute('INSERT INTO cards (ID, ReceivingPlayer, wasYellowCard) VALUES (?, ?, ?)',(cardId[0], cardData[0], cardData[2]))

    for goalData in goalsData:
        goalId = db.execute('INSERT INTO events (MatchID, Minute, eventCategoryID) VALUES (?, ?, ?) RETURNING eventID',(matchID, goalData[1], 1)).fetchone()
        db.execute('INSERT INTO goals (ID, Scorer_ID, was_Penalty, was_Owngoal) VALUES (?, ?, ?, ?)',(goalId[0], goalData[0], goalData[2], goalData[3]))

    db.execute('UPDATE season SET HomeGoals=?, AwayGoals=?, Result=?, Is_Finished=1 WHERE MatchID=?',(homeGoals, awayGoals, matchResult, matchID))
    db.commit()
    flash("Result added successfully")

    return redirect(url_for('dashboard.admintools'))

@bp.route('/admintools/delete-results', methods=('POST',))
@login_required
@admin_required
def delete_results():
    db = get_db()
    if request.method == 'POST':
        matchID = int(request.form['matchID'])
    error = None
    if not matchID:
        error = 'Select a Match'
        flash(error)
        return redirect(url_for('dashboard.admintools'))

    # Delete Match result
    db.execute('UPDATE season SET HomeGoals=NULL, AwayGoals=NULL, Result=NULL, Is_Finished=0 WHERE MatchID=?',(matchID,))

    events = db.execute('SELECT eventID, eventCategoryID FROM events WHERE MatchID=?',(matchID,)).fetchall()

    for event in events:
        if event['eventCategoryID'] == 1:
            # Delete Goal
            db.execute('DELETE FROM goals WHERE ID=?',(event['eventID'],))
        elif event['eventCategoryID'] == 2:
            # Delete Card
            db.execute('DELETE FROM cards WHERE ID=?',(event['eventID'],))
        else:
            flash(r"Unknown Event Category: {event['eventCategoryID']}")
    
    db.execute('DELETE FROM events WHERE MatchID=?',(matchID,))

    db.commit()
    flash("Result deleted successfully")

    return redirect(url_for('dashboard.admintools'))

@bp.route('/admintools/generate-schedule', methods=('POST',))
@login_required
@admin_required
def generate_schedule():
    if request.method == 'POST':
        numSeasons = int(request.form['numSeasons'])
        print(f"Num Seasons: {numSeasons}")
        try:
            request.form['withReturnMatch']
        except KeyError:
            withReturnMatch = False
        else:
            withReturnMatch = True

        error = None
        if not numSeasons:
            error = 'numSeasons is required.'
        if error is not None:
            flash(error)
            return redirect(url_for('dashboard.admintools'))
    
    db = get_db()
    generateSchedule(db, numSeasons, withReturnMatch)
    flash("Schedule generated Successfully")
    return redirect(url_for('dashboard.admintools'))        

@bp.route('/admintools/delete-schedule', methods=('POST',))
@login_required
@admin_required
def delete_schedule():
    db = get_db()
    db.execute("DELETE FROM season")
    db.execute("DELETE FROM events")
    db.execute("DELETE FROM goals")
    db.execute("DELETE FROM cards")
    db.commit()
    flash("Schedule deleted successfully")
    return redirect(url_for('dashboard.admintools'))        

@bp.route('/admintools/add-player-to-team', methods=('POST',))
@login_required
@admin_required
def add_player_to_team():
    if request.method == 'POST':
        try:
            playerID = int(request.form['playerID'])
            teamID = int(request.form['teamID'])
        except BadRequestKeyError:
            error = 'Error - There was no Player selected'
            flash(error)
            return redirect(url_for('dashboard.admintools'))
        
        error = None
        if not playerID:
            error = 'PlayerID is required.'
        if not teamID:
            error = 'teamID is required.'
        if error is not None:
            flash(error)
            return redirect(url_for('dashboard.admintools'))

    db = get_db()
    if db.execute('SELECT COUNT(team_player.teamID) FROM team_player WHERE teamID = ?',(teamID,)).fetchone() == 18:
        flash("Maximum Number of Players already reached")
        return redirect(url_for('dashboard.admintools'))
    if db.execute('SELECT COUNT(team_player.playerID) FROM team_player WHERE playerID = ?',(playerID,)).fetchone()[0]:
        flash("Player is already member of another Team!")
        return redirect(url_for('dashboard.admintools'))
    faceImageUrl = db.execute('SELECT player_face_url from players WHERE ID=?',(playerID,)).fetchone()[0]
    if not(downloadPlayerImage(playerID, faceImageUrl)):
        flash("Player Image could not be downloaded")
    db.execute('INSERT INTO team_player (teamID, playerID) VALUES (?,?)',(teamID, playerID))
    db.commit()
    flash("Player was added successfully")
    return redirect(url_for('dashboard.admintools'))

@bp.route('/admintools/delete-player-from-team', methods=('POST',))
@login_required
@admin_required
def delete_player_from_team():
    if request.method == 'POST':
        playerID = int(request.form['playerID'])
        error = None
        if not playerID:
            error = 'playerID is required.'
        if error is not None:
            flash(error)
            return redirect(url_for('dashboard.admintools'))
    db = get_db()
    db.execute('DELETE FROM team_player WHERE playerID = ?',(playerID,))
    db.commit()
    flash("Player was removed successfully")
    return redirect(url_for('dashboard.admintools'))

@bp.route('/admintools/delete-gamer-from-tournament', methods=('POST',))
@login_required
@admin_required
def delete_gamer_from_tournament():
    if request.method == 'POST':
        gamerID = int(request.form['gamerID'])
        error = None
        if not gamerID:
            error = 'gamerID is required.'
        if error is not None:
            flash(error)
            return redirect(url_for('dashboard.admintools'))
    
    db = get_db()
    if db.execute('SELECT isAdmin FROM gamer WHERE ID =?',(gamerID,)).fetchone()[0]:
        flash("Can't delete Gamer, as this Gamer is an admin")
        return redirect(url_for('dashboard.admintools'))
    db.execute('DELETE FROM gamer WHERE ID = ?',(gamerID,))
    db.commit()
    flash("Gamer deleted successfully")
    return redirect(url_for('dashboard.admintools'))