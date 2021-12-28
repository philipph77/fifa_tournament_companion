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
    table_column_names = ['Team', 'Games Played', 'Wins', 'Draws', 'Losses', 'Goals For', 'Goals Against', 'Goal Difference', 'Points']
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
            'Games Played': total_games_played,
            'Wins': total_wins,
            'Draws': total_draws,
            'Losses': total_defeats,
            'Goals For': total_scored_goals,
            'Goals Against': total_against_goals,
            'Goal Difference': total_scored_goals- total_against_goals,
            'Points': total_points
            },
            ignore_index=True)
        table.sort_values(by=['Points', 'Goal Difference', 'Goals For', 'Wins'], ascending=False, inplace=True)
        home_table = home_table.append({
            'Team': team_name,
            'Games Played': home_games_played,
            'Wins': home_wins,
            'Draws': home_draws,
            'Losses': home_defeats,
            'Goals For': home_scored_goals,
            'Goals Against': home_against_goals,
            'Goal Difference': home_scored_goals- home_against_goals,
            'Points': home_points
            },
            ignore_index=True)
        home_table.sort_values(by=['Points', 'Goal Difference', 'Goals For', 'Wins'], ascending=False, inplace=True)
        away_table = away_table.append({
            'Team': team_name,
            'Games Played': away_games_played,
            'Wins': away_wins,
            'Draws': away_draws,
            'Losses': away_defeats,
            'Goals For': away_scored_goals,
            'Goals Against': away_against_goals,
            'Goal Difference': away_scored_goals- away_against_goals,
            'Points': away_points
            },
            ignore_index=True)
        away_table.sort_values(by=['Points', 'Goal Difference', 'Goals For', 'Wins'], ascending=False, inplace=True)
    
    table.reset_index(drop=True, inplace=True)
    table.index +=1
    home_table.reset_index(drop=True, inplace=True)
    home_table.index +=1
    away_table.reset_index(drop=True, inplace=True)
    away_table.index +=1

    return table, home_table, away_table

def calculateScorerStats(db):
    scorer = db.execute('SELECT players.short_name, COUNT(*) AS `points` FROM goals LEFT JOIN players on players.ID = goals.Scorer_ID WHERE goals.was_Owngoal=0 GROUP BY Scorer_ID ORDER BY points DESC LIMIT 10')
    scorer = pd.DataFrame(data=scorer.fetchall(), columns=['Player', 'Goals'])
    scorer.sort_values('Goals', ascending=False, inplace=True)
    scorer.reset_index(drop=True, inplace=True)
    scorer.index +=1
    assist =db.execute('SELECT players.short_name, COUNT(*) AS `points` FROM goals LEFT JOIN players on players.ID = goals.Wingman_ID WHERE goals.was_Owngoal=0 AND goals.Wingman_ID IS NOT NULL GROUP BY Wingman_ID ORDER BY points DESC LIMIT 10')
    assist = pd.DataFrame(data=assist.fetchall(), columns=['Player', 'Assists'])
    assist.sort_values('Assists', ascending=False, inplace=True)
    assist.reset_index(drop=True, inplace=True)
    assist.index +=1
    penaldo = db.execute('SELECT players.short_name, COUNT(*) AS `points` FROM goals LEFT JOIN players on players.ID = goals.Scorer_ID WHERE goals.was_Owngoal=0 AND goals.was_Penalty=1 GROUP BY Scorer_ID ORDER BY points DESC LIMIT 10')        
    penaldo = pd.DataFrame(data=penaldo.fetchall(), columns=['Player', 'Penalties'])
    penaldo.sort_values('Penalties', ascending=False, inplace=True)
    penaldo.reset_index(drop=True, inplace=True)
    penaldo.index +=1
    
    return scorer, assist, penaldo

def calculateCardStats(db):
    # cardCategories:
    # 1 - Yellow Card,
    # 3 - YellowRed Card,
    # 5 - Red Card
    gamer_ids = db.execute('SELECT ID FROM gamer').fetchall()
    gamer_ids = [int(id[0]) for id in gamer_ids]
    yellow_cards = db.execute('SELECT players.short_name, COUNT(*) AS `points` FROM cards LEFT JOIN players on players.ID = cards.ReceivingPlayer WHERE cards.cardCategory=1 GROUP BY ReceivingPlayer ORDER BY points DESC LIMIT 10')
    yellow_cards = pd.DataFrame(data=yellow_cards.fetchall(), columns=['Name', 'Yellow Cards'])
    yellow_cards.sort_values(yellow_cards.columns[1], ascending=False, inplace=True)
    yellow_cards.reset_index(drop=True, inplace=True)
    yellow_cards.index +=1
    red_cards = db.execute('SELECT players.short_name, COUNT(*) AS `points` FROM cards LEFT JOIN players on players.ID = cards.ReceivingPlayer WHERE cards.cardCategory=5 GROUP BY ReceivingPlayer ORDER BY points DESC LIMIT 10')
    red_cards = pd.DataFrame(data=red_cards.fetchall(), columns=['Name', 'Red Cars'])
    red_cards.sort_values(red_cards.columns[1], ascending=False, inplace=True)
    red_cards.reset_index(drop=True, inplace=True)
    red_cards.index +=1
    
    return yellow_cards, red_cards

def calculateFairnessTable(db):
    # cardCategories:
    # 1 - Yellow Card,
    # 3 - YellowRed Card,
    # 5 - Red Card
    stats = db.execute(
        """SELECT gamer.TeamName,
        SUM(cards.cardCategory) as points,
        SUM(cards.cardCategory=5) as reds,
        SUM(cards.cardCategory=3) as yrs,
        SUM(cards.cardCategory=1) as yellows
        FROM gamer
        LEFT JOIN team_player ON gamer.ID= team_player.teamID
        LEFT JOIN cards ON cards.ReceivingPlayer=team_player.playerID
        GROUP BY team_player.teamID
        ORDER BY points, reds, yrs, yellows ASC"""
    ).fetchall()
    statsDf = pd.DataFrame(data=stats, columns=["Team Name", "Points", "Red Cards", "Yellow-Red Cards", "Yellow Cards"])
    statsDf.fillna(0, inplace=True, downcast='infer')
    statsDf.sort_values(["Points", "Red Cards", "Yellow-Red Cards", "Yellow Cards"], ascending=False, inplace=True)
    statsDf.reset_index(drop=True, inplace=True)
    statsDf.index +=1
    return statsDf



def getWholeSchedule(db):
    schedule = db.execute('''
        SELECT MatchDay, team1.TeamName, team2.TeamName, ifnull(HomeGoals, '-' ), ifnull(AwayGoals, '-' )
        FROM season
        LEFT JOIN gamer team1 ON season.HomeTeamID=team1.ID
        LEFT JOIN gamer team2 ON season.AwayTeamID=team2.ID
    ''')
    schedule = pd.DataFrame(data=schedule.fetchall(), columns=[ 'MatchDay', 'HomeTeam', 'AwayTeam', 'HomeGoals', 'AwayGoals'])
    
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
                        AND (season.HomeTeamID=?
                        OR season.AwayTeamID=?)
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


def updateTableforMatchDay(db, matchDay, table):
    games = db.execute("SELECT HomeTeamID, AwayTeamID, Result, HomeGoals, AwayGoals FROM season WHERE MatchDay=?",(matchDay,)).fetchall()
    for game in games:
        # Adujust Scored Goals and Goal Difference
        table.loc[table.teamID==game['HomeTeamID'], "ScoredGoals"] += game["HomeGoals"]
        table.loc[table.teamID==game['HomeTeamID'], "GoalDifference"] += game["HomeGoals"] - game["AwayGoals"]
        table.loc[table.teamID==game['AwayTeamID'], "ScoredGoals"] += game["AwayGoals"]
        table.loc[table.teamID==game['AwayTeamID'], "GoalDifference"] += game["AwayGoals"] - game["HomeGoals"]
        if game['Result'] == 0:
            # Draw
            table.loc[table.teamID==game['HomeTeamID'], "Points"] += 1
            table.loc[table.teamID==game['AwayTeamID'], "Points"] += 1
        elif game['Result'] == 1:
            # Home Team Won
            table.loc[table.teamID==game['HomeTeamID'], "Points"] += 3
            table.loc[table.teamID==game['HomeTeamID'], "Wins"] += 1
        elif game['Result'] == 2:
            # Away Team Won
            table.loc[table.teamID==game['AwayTeamID'], "Points"] += 3
            table.loc[table.teamID==game['AwayTeamID'], "Wins"] += 1
        else:
            raise NotImplementedError
    
    table.sort_values(by=['Points', 'GoalDifference', 'ScoredGoals', 'Wins'], ascending=False, inplace=True)
    table.reset_index(drop=True, inplace=True)
    table.index +=1

    return table


def getPositionsLineChartData(db):
    maxMatchDay = db.execute("SELECT MAX(MatchDay) FROM season WHERE Is_Finished=1").fetchone()[0]
    teams = db.execute("SELECT ID, TeamName FROM gamer").fetchall()
    colors = ["#7f1d1d", "#7c2d12", "#78350f", "#365314", "#064e3b", "#164e63", "#1e3a8a", "#4c1d95", "#701a75", "#881337"]
    # prepare Table
    teamsData = db.execute("SELECT ID, 0, 0, 0, 0 FROM gamer").fetchall()
    table = pd.DataFrame(teamsData, columns=["teamID", "Points", "GoalDifference", "ScoredGoals", "Wins"])
    table.index +=1
    lineChartLabels = list(range(1, maxMatchDay+1))
    # prepare LineCharts Datasets
    lineChartDatasets = []
    for i,team in enumerate(teams):
        lineChartDatasets.append({
            "teamID": team["ID"],
            "name": team["TeamName"],
            "positions": [],
            "color": colors[i%10]
        })

    for matchDay in range(1,maxMatchDay+1):
        table = updateTableforMatchDay(db, matchDay, table)
        for team in lineChartDatasets:
            team["positions"].append(table.loc[table.teamID==team["teamID"]].index[0])


    return lineChartLabels, lineChartDatasets