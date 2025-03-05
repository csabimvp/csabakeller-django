import json


def annual_team_analysis(team):
    # Loading JSON Database
    f = open("/home/csabimvp/mywebsite/webscrapers/nba_game_scores.json")
    data = json.load(f)

    f2 = open("/home/csabimvp/mywebsite/webscrapers/nba_teams.json")
    teams = json.load(f2)
    team_short = teams[team][0]
    team_long = teams[team][1]

    # Creating GP List and Dictionary to store data.
    games_played = []
    game_dict = {
        "team_searched": "",
        "win": "",
        "date": "",
        "winner_team": "",
        "winner_score": "",
        "loser_team": "",
        "loser_score": "",
        "game_type": "",
        "links": "",
    }
    analytics = {
        "wins": 0,
        "losses": 0,
        "points_scored": 0,
        "points_allowed": 0,
    }

    # Looping trough games to get information for the team query
    for dates in data.keys():
        for games in data[dates]["games_data"]:
            if games["winner_team"] == team_short:
                game_dict = {
                    "team_searched": team_long,
                    "win": True,
                    "date": dates,
                    "winner_team": team_long,
                    "winner_score": int(games["winner_score"]),
                    "loser_team": games["loser_team"],
                    "loser_score": int(games["loser_score"]),
                    "game_type": games["game_type"],
                    "links": games["links"],
                }
                analytics["wins"] += 1
                analytics["points_scored"] += int(games["winner_score"])
                analytics["points_allowed"] += int(games["loser_score"])
                games_played.append(game_dict)
            elif games["loser_team"] == team_short:
                game_dict = {
                    "team_searched": team_long,
                    "win": False,
                    "date": dates,
                    "winner_team": games["winner_team"],
                    "winner_score": int(games["winner_score"]),
                    "loser_team": team_long,
                    "loser_score": int(games["loser_score"]),
                    "game_type": games["game_type"],
                    "links": games["links"],
                }
                analytics["losses"] += 1
                analytics["points_scored"] += int(games["loser_score"])
                analytics["points_allowed"] += int(games["winner_score"])
                games_played.append(game_dict)
            else:
                pass

    analytics["games_played"] = analytics["wins"] + analytics["losses"]
    analytics["win_percent"] = round(analytics["wins"] / analytics["games_played"], 2)
    analytics["plus_minus"] = analytics["points_scored"] - analytics["points_allowed"]
    analytics["plus_minus_per_game"] = round(
        analytics["plus_minus"] / analytics["games_played"], 2
    )

    response = {"analytics": analytics, "games_played": games_played}

    return response


def season_leaders_table():
    f = open("/home/csabimvp/mywebsite/webscrapers/player_stats_database.json")
    data = json.load(f)

    return data
