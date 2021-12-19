import pandas as pd
import requests
from os import path
import shutil

def getTeamStats(db, gamerID):
    res = db.execute('SELECT (players.short_name, players.player_position, players.value_eur, age) FROM team_player JOIN players ON players.ID=team_player.playerID WHERE team_player.teamID = ?',(gamerID)).fetchall()
    desc = db.description
    column_names = [col[0] for col in desc]
    teamStats = [dict(zip(column_names, row)) for row in res]
    return teamStats


def calculateTables(db):
     # Punkte, Tore, Gegentore, Siege, Unentschieden, Niederlagen
    table_column_names = ['Team', 'GamesPlayed', 'Wins', 'Draws', 'Losses', 'Goals_For', 'Goals_Against', 'Goal_Difference', 'Points']
    table = pd.DataFrame(columns=table_column_names)
    home_table = pd.DataFrame(columns=table_column_names)
    away_table = pd.DataFrame(columns=table_column_names)
    gamer_ids_res = db.execute("SELECT ID FROM gamer").fetchall()
    gamer_ids = [int(id[0]) for id in gamer_ids_res]
    for gamer_id in gamer_ids:
        team_name = db.execute('SELECT TeamName FROM gamer WHERE ID=?',(gamer_id,)).fetchone()[0]
        home_games_played = db.execute('SELECT COUNT(Result) FROM season WHERE HomeTeamID = ? AND Is_Finished=1',(gamer_id,)).fetchone()[0]
        away_games_played = db.execute('SELECT COUNT(Result) FROM season WHERE AwayTeamID =? AND Is_Finished=1',(gamer_id,)).fetchone()[0]
        home_wins = db.execute('SELECT COUNT(Result) FROM season WHERE HomeTeamID=? AND Is_Finished=1 AND Result=1',(gamer_id,)).fetchone()[0]
        away_wins = db.execute('SELECT COUNT(Result) FROM season WHERE AwayTeamID=? AND Is_Finished=1 AND Result=2',(gamer_id,)).fetchone()[0]
        home_defeats = db.execute('SELECT COUNT(Result) FROM season WHERE HomeTeamID=? AND Is_Finished=1 AND Result=2',(gamer_id,)).fetchone()[0]
        away_defeats = db.execute('SELECT COUNT(Result) FROM season WHERE AwayTeamID=? AND Is_Finished=1 AND Result=1',(gamer_id,)).fetchone()[0]
        home_draws = db.execute('SELECT COUNT(Result) FROM season WHERE HomeTeamID=? AND Is_Finished=1 AND Result=0',(gamer_id,)).fetchone()[0]
        away_draws = db.execute('SELECT COUNT(Result) FROM season WHERE AwayTeamID=? AND Is_Finished=1 AND Result=0',(gamer_id,)).fetchone()[0]
        home_wins = int(home_wins or 0)
        away_wins = int(away_wins or 0)
        home_defeats = int(home_defeats or 0)
        away_defeats = int(away_defeats or 0)
        home_draws = int(home_draws or 0)
        away_wins = int(away_wins or 0)
        home_scored_goals = db.execute('SELECT SUM(HomeGoals) FROM season WHERE HomeTeamID=? AND Is_Finished=1',(gamer_id,)).fetchone()[0]
        away_scored_goals = db.execute('SELECT SUM(AwayGoals) FROM season WHERE AwayTeamID=? AND Is_Finished=1',(gamer_id,)).fetchone()[0]
        home_against_goals = db.execute('SELECT SUM(AwayGoals) FROM season WHERE HomeTeamID=? AND Is_Finished=1',(gamer_id,)).fetchone()[0]
        away_against_goals = db.execute('SELECT SUM(HomeGoals) FROM season WHERE AwayTeamID=? AND Is_Finished=1',(gamer_id,)).fetchone()[0]
        home_scored_goals = int(home_scored_goals or 0)
        away_scored_goals = int(away_scored_goals or 0)
        home_against_goals = int(home_against_goals or 0)
        away_against_goals = int(away_against_goals or 0)
        home_points = 3*home_wins + home_draws
        away_points = 3*away_wins + away_draws
        total_games_played = home_games_played + away_games_played
        total_wins = home_wins + away_wins
        total_defeats = home_defeats + away_defeats
        total_draws = home_draws + away_draws
        total_points = home_points + away_points
        total_scored_goals = home_scored_goals + away_scored_goals
        total_against_goals = home_against_goals + away_against_goals
        table = table.append({
            'Team': team_name,
            'GamesPlayed': total_games_played,
            'Wins': total_wins,
            'Draws': total_draws,
            'Losses': total_defeats,
            'Goals_For': total_scored_goals,
            'Goals_Against': total_against_goals,
            'Goal_Difference': total_scored_goals- total_against_goals,
            'Points': total_points
            },
            ignore_index=True)
        table.sort_values('Points', ascending=False, inplace=True)
        home_table = home_table.append({
            'Team': team_name,
            'GamesPlayed': home_games_played,
            'Wins': home_wins,
            'Draws': home_draws,
            'Losses': home_defeats,
            'Goals_For': home_scored_goals,
            'Goals_Against': home_against_goals,
            'Goal_Difference': home_scored_goals- home_against_goals,
            'Points': home_points
            },
            ignore_index=True)
        home_table.sort_values('Points', ascending=False, inplace=True)
        away_table = away_table.append({
            'Team': team_name,
            'GamesPlayed': away_games_played,
            'Wins': away_wins,
            'Draws': away_draws,
            'Losses': away_defeats,
            'Goals_For': away_scored_goals,
            'Goals_Against': away_against_goals,
            'Goal_Difference': away_scored_goals- away_against_goals,
            'Points': away_points
            },
            ignore_index=True)
        away_table.sort_values('Points', ascending=False, inplace=True)
    
    table.index +=1
    home_table.index +=1
    away_table.index +=1

    return table, home_table, away_table

def calculateScorerStats(db):
    scorer = db.execute('SELECT players.short_name, COUNT(*) AS `points` FROM goals LEFT JOIN players on players.ID = goals.Scorer_ID WHERE goals.was_Owngoal=0 GROUP BY Scorer_ID')
    scorer = pd.DataFrame(data=scorer.fetchall(), columns=['Player', 'Goals'])
    scorer.sort_values('Goals', ascending=False, inplace=True)
    assist =db.execute('SELECT players.short_name, COUNT(*) AS `points` FROM goals LEFT JOIN players on players.ID = goals.Wingman_ID WHERE goals.was_Owngoal=0 AND goals.Wingman_ID IS NOT NULL GROUP BY Wingman_ID')
    assist = pd.DataFrame(data=assist.fetchall(), columns=['Player', 'Assists'])
    assist.sort_values('Assists', ascending=False, inplace=True)
    penaldo = db.execute('SELECT players.short_name, COUNT(*) AS `points` FROM goals LEFT JOIN players on players.ID = goals.Scorer_ID WHERE goals.was_Owngoal=0 AND goals.was_Penalty=1 GROUP BY Scorer_ID')        
    penaldo = pd.DataFrame(data=penaldo.fetchall(), columns=['Player', 'Penalties'])
    penaldo.sort_values('Penalties', ascending=False, inplace=True)
    
    return scorer, assist, penaldo

def calculateCardStats(db):
    gamer_ids = db.execute('SELECT ID FROM gamer').fetchall()
    gamer_ids = [int(id[0]) for id in gamer_ids]
    yellow_cards = db.execute('SELECT players.short_name, COUNT(*) AS `points` FROM cards LEFT JOIN players on players.ID = cards.ReceivingPlayer WHERE cards.wasYellowCard=1 GROUP BY ReceivingPlayer')
    yellow_cards = pd.DataFrame(data=yellow_cards.fetchall(), columns=['Name', 'Yellow Cards'])
    yellow_cards.sort_values(yellow_cards.columns[1], ascending=False, inplace=True)
    red_cards = db.execute('SELECT players.short_name, COUNT(*) AS `points` FROM cards LEFT JOIN players on players.ID = cards.ReceivingPlayer WHERE cards.wasYellowCard=0 GROUP BY ReceivingPlayer')
    red_cards = pd.DataFrame(data=red_cards.fetchall(), columns=['Name', 'Red Cars'])
    red_cards.sort_values(red_cards.columns[1], ascending=False, inplace=True)
    
    return yellow_cards, red_cards


def getWholeSchedule(db):
    schedule = db.execute('''
        SELECT MatchDay, team1.TeamName, team2.TeamName
        FROM season
        LEFT JOIN gamer team1 ON season.HomeTeamID=team1.ID
        LEFT JOIN gamer team2 ON season.AwayTeamID=team2.ID
        WHERE season.Is_Finished = 0
    ''')
    schedule = pd.DataFrame(data=schedule.fetchall(), columns=[ 'MatchDay', 'HomeTeam', 'AwayTeam'])
    
    return schedule

def getUpcomingGames(db, n_games=20):
    current_matchday = db.execute("SELECT MIN(MatchDay) FROM season WHERE Is_Finished = 0").fetchone()[0]
    print(f"Current Machtday {current_matchday}")
    upcoming_games = db.execute('''
        SELECT MatchDay, team1.TeamName, team2.TeamName
        FROM season
        LEFT JOIN gamer team1 ON season.HomeTeamID=team1.ID
        LEFT JOIN gamer team2 ON season.AwayTeamID=team2.ID
        WHERE season.Is_Finished = 0
        AND season.MatchDay <= ?
        LIMIT ?'''
        ,(current_matchday, n_games)
    )
    upcoming_games = pd.DataFrame(data=upcoming_games.fetchall(), columns=['MatchDay', 'HomeTeam', 'AwayTeam'])
    
    return upcoming_games

def generateSchedule(db, numSeasons, withReturnMatch):
    # https://gist.github.com/ih84ds/be485a92f334c293ce4f1c84bfba54c9
    for season_idx in range(1,numSeasons+1):
        schedule = []
        teams = []
        res = db.execute("SELECT ID FROM gamer").fetchall()
        for row in res:
            teams.append(row[0])
        if len(teams) % 2 == 1:
            teams = teams + [None]
        n = len(teams)
        map = list(range(n))
        mid = n // 2
        for i in range(n-1):
            l1 = map[:mid]
            l2 = map[mid:]
            l2.reverse()
            round = []
            for j in range(mid):
                t1 = teams[l1[j]]
                t2 = teams[l2[j]]
                if j == 0 and i % 2 == 1:
                    # flip the first match only, every other round
                    # (this is because the first match always involves the last player in the list)
                    round.append((t2, t1))
                else:
                    round.append((t1, t2))
            schedule.append(round)
            # rotate list by n/2, leaving last element at the end
            map = map[mid:-1] + map[:mid] + map[-1:]
        for match_day_idx, match_day in enumerate(schedule):
            match_day_idx = match_day_idx + 1 + (season_idx-1)*2*len(schedule)
            for match in match_day:
                if not(match[0]==None) and not(match[1]==None):
                    db.execute('INSERT INTO season (HomeTeamID, AwayTeamID, MatchDay, IsFirstLeg, Season) VALUES (?, ?, ?, 1, ?)',(match[0], match[1], match_day_idx, season_idx))
        if withReturnMatch:
            return_schedule = [[(match[1], match[0]) for match in match_day] for match_day in schedule]
            for match_day_idx, match_day in enumerate(return_schedule):
                match_day_idx = match_day_idx + 1+ (season_idx-1)*2*len(schedule) + len(schedule)
                for match in match_day:
                    if not(match[0]==None) and not(match[1]==None):
                        db.execute('INSERT INTO season (HomeTeamID, AwayTeamID, MatchDay, IsFirstLeg, Season) VALUES (?, ?, ?, 0, ?)',(match[0], match[1], match_day_idx, season_idx))
    db.commit()
    return

def getMarketValueOfTeam(db, teamId):
    return db.execute('SELECT ifnull(SUM(players.value_eur), 0) FROM team_player JOIN players ON players.ID=team_player.playerID WHERE team_player.teamID=?',(teamId,)).fetchone()[0]

def getStrengthOfTeam(db, teamId):
    return db.execute('SELECT ifnull(AVG(players.overall), 0) FROM team_player JOIN players ON players.ID=team_player.playerID WHERE team_player.teamID=?',(teamId,)).fetchone()[0]

def getNextGamesOfTeam(db, teamId):
    res =  db.execute(
                        '''SELECT MatchDay, team1.TeamName, team2.TeamName
                        FROM season
                        LEFT JOIN gamer team1 ON season.HomeTeamID=team1.ID
                        LEFT JOIN gamer team2 ON season.AwayTeamID=team2.ID
                        WHERE season.Is_Finished=0
                        AND season.HomeTeamID=?
                        OR season.AwayTeamID=?
                        LIMIT 10''',
                        (teamId, teamId)
                    )
    return pd.DataFrame(data=res.fetchall(), columns=[ 'MatchDay', 'HomeTeam', 'AwayTeam'])

def downloadPlayerImage(playerID, faceImageUrl):
    filename = f"{playerID}.png"
    r = requests.get(faceImageUrl, stream=True)
    if r.status_code == 200:
        with open(path.join("ftc", "static", "faces", filename), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        return 1
    else:
        return 0