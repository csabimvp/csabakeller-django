import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup, Comment
from googleapiclient.discovery import build


def nba_scoreboard_scraper(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    games = soup.find_all("div", {"class": "game_summary expanded nohover"})

    date = soup.find("span", {"class": "button2 index"}).get_text()

    games_data = []

    for game in games:
        dict = {}
        winner_team = game.find("tr", {"class": "winner"}).td.get_text()
        loser_team = game.find("tr", {"class": "loser"}).td.get_text()
        score1 = game.find_all("td", {"class": "right"})[0].get_text()
        score2 = game.find_all("td", {"class": "right"})[2].get_text()
        all_links = [
            "https://www.basketball-reference.com" + tag["href"]
            for tag in game.select("p a[href]")
        ]

        if int(score1) > int(score2):
            winner_score = score1
            loser_score = score2
        else:
            winner_score = score2
            loser_score = score1

        if len(game.find_all("td", {"class": "right"})[3].get_text()) == 6:
            overtime = "overtime"
        else:
            overtime = "no_overtime"

        dict["winner_team"] = winner_team
        dict["loser_team"] = loser_team
        dict["winner_score"] = winner_score
        dict["loser_score"] = loser_score
        dict["overtime"] = overtime
        dict["hooper_video_id"] = ""
        dict["motion_video_id"] = ""
        dict["links"] = all_links

        games_data.append(dict)

    return games_data, date


def nba_stats_daily_leaders_scraper(url):
    response = requests.get(url)
    data = json.loads(response.text)

    lookups = {
        "0": "PTS",
        "1": "REB",
        "2": "AST",
        "3": "BLK",
        "4": "STL",
        "5": "TOV",
        "6": "FG3M",
        "7": "FTM",
    }

    daily_player_stats = {
        "PTS": [],
        "REB": [],
        "AST": [],
        "BLK": [],
        "STL": [],
        "TOV": [],
        "FG3M": [],
        "FTM": [],
    }

    for category in range(8):
        cat_str = str(category)
        for player in range(5):
            details = []
            player_name = data["items"][0]["items"][category]["playerstats"][player][
                "PLAYER_NAME"
            ]
            team = data["items"][0]["items"][category]["playerstats"][player][
                "TEAM_ABBREVIATION"
            ]
            category_lookup = lookups[cat_str]
            value = data["items"][0]["items"][category]["playerstats"][player][
                category_lookup
            ]

            details.append(player_name)
            details.append(team)
            details.append(category_lookup)
            details.append(value)

            daily_player_stats[category_lookup].append(details)

    return daily_player_stats


def nba_standings_scraper(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    # Scraping Eastern and Western conference tables.
    eastern_conf_table = soup.find("table", id="confs_standings_E")
    western_conf_table = soup.find("table", id="confs_standings_W")

    eastern_rows = eastern_conf_table.find_all("tr")
    eastern_rows.pop(0)
    western_rows = western_conf_table.find_all("tr")
    western_rows.pop(0)

    # Creating dictionary to store data.
    nba_standings_2021_22 = {"eastern_conference": [], "western_conference": []}

    # Looping trough the eastern conference table to get data.
    for row in eastern_rows:
        eastern_df = {}
        team_name = row.find("th", {"data-stat": "team_name"}).get_text()[:3]
        wins = row.find("td", {"data-stat": "wins"}).get_text()
        losses = row.find("td", {"data-stat": "losses"}).get_text()
        games_played = int(wins) + int(losses)

        try:
            pct = round(1 - (int(losses) / games_played), 3)
        except ZeroDivisionError:
            pct = 0

        eastern_df["team_name"] = team_name
        eastern_df["wins"] = wins
        eastern_df["losses"] = losses
        eastern_df["games_played"] = games_played
        eastern_df["pct"] = pct

        nba_standings_2021_22["eastern_conference"].append(eastern_df)

    # Looping trough the western conference table to get data.
    for row in western_rows:
        western_df = {}
        team_name = row.find("th", {"data-stat": "team_name"}).get_text()[:3]
        wins = row.find("td", {"data-stat": "wins"}).get_text()
        losses = row.find("td", {"data-stat": "losses"}).get_text()
        games_played = int(wins) + int(losses)

        try:
            pct = round(1 - (int(losses) / games_played), 3)
        except ZeroDivisionError:
            pct = 0

        western_df["team_name"] = team_name
        western_df["wins"] = wins
        western_df["losses"] = losses
        western_df["games_played"] = games_played
        western_df["pct"] = pct

        nba_standings_2021_22["western_conference"].append(western_df)

    return nba_standings_2021_22


def team_contracts(team):
    url = f"https://www.basketball-reference.com/contracts/{team}.html"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    salary_table = soup.find("table", {"id": "contracts"})

    # Getting Table information from BeautifulSoup.
    salary_col_headers_html = salary_table.thead.find_all("th")
    salary_col_data_html = salary_table.tbody.find_all("tr")

    # Getting Table headers.
    salary_col_headers = []
    for column in salary_col_headers_html:
        value = column.get_text()
        salary_col_headers.append(value)

    # Response contains double header, we don't need that and "\xa0" and we don't need either.
    # salary_col_headers.remove("\xa0")
    salary_col_headers.remove("\xa0")
    salary_col_headers.remove("")
    salary_col_headers.remove("Salary")

    # Getting Table data.
    salary_table_data = []
    for srow in salary_col_data_html:
        srow_data = []
        try:
            name = srow.find("th").get_text()
        except:
            pass
        srow_data.append(name)
        sdata = srow.find_all("td")
        for sd in sdata:
            srow_data.append(sd.get_text())

        # Dropping rows with WhiteSpace - not intrested.
        if len(srow_data) == 9:
            salary_table_data.append(srow_data)
        else:
            pass

    data = {"headers": salary_col_headers, "row_data": salary_table_data}

    return data


def team_player_stats(team):
    # print(team)
    url = f"https://www.basketball-reference.com/teams/{team}/2024.html"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    # Getting Totals Table information from BeautifulSoup.
    total_table = soup.find("table", {"id": "totals"})
    col_headers_html = total_table.thead.find_all("th")
    col_data_html = total_table.tbody.find_all("tr")

    # Getting Total Table headers.
    col_headers = []
    for count, col in enumerate(col_headers_html):
        if count == 1:
            value = "Name"
            col_headers.append(value)
        else:
            value = col.get_text()
            col_headers.append(value)

    # Response contains RK column, we don't need that
    col_headers.remove("Rk")

    # Adding custom column headers.
    col_headers.append("ppg")

    # Getting Total Table data.
    players = []
    for row in col_data_html:
        rdata = row.find_all("td")
        row_data = []
        for d in rdata:
            row_data.append(d.get_text())

        players.append(row_data)

    # new list for response dictionary keys, because the original ones are not usable due to special characters.
    dict_headers = [
        "name",
        "age",
        "games_played",
        "games_started",
        "minutes_played",
        "fg",
        "fga",
        "fgprecent",
        "threepoint",
        "threepointa",
        "threepoint_precent",
        "twopoint",
        "twopointa",
        "twopoint_precent",
        "efg",
        "ft",
        "fta",
        "ftprecent",
        "orb",
        "drb",
        "trb",
        "ast",
        "stl",
        "blk",
        "tov",
        "personal_fouls",
        "pts",
    ]

    # Creating list of dictionary response, where the numbers are INT or FLOAT. for filtering, sorting purposes.
    table_data = []
    for player in players:
        row_dict = {}
        for i, colll in enumerate(dict_headers):
            if i == 0:
                row_dict[colll] = player[i]
            else:
                try:
                    row_dict[colll] = int(player[i])
                except ValueError:
                    if player[i] == "":
                        row_dict[colll] = 0
                    else:
                        row_dict[colll] = float(player[i])

        # Calculating player Point Per Game Statistics.
        if row_dict["pts"] != 0:
            ppg = round(float(row_dict["pts"] / row_dict["games_played"]), 2)
            row_dict["ppg"] = ppg
        else:
            ppg = 0
            row_dict["ppg"] = ppg

        # Adding Player Stats to the table data list.
        table_data.append(row_dict)

    # Getting Injury Table information from BeautifulSoup.
    tables = []
    for comments in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comment_soup = BeautifulSoup(comments, "html.parser")
        res_table = comment_soup.find("table", {"id": "injuries"})
        if res_table != None:
            tables.append(res_table)
        else:
            pass

    # Check if there are injuries in the team.
    if len(tables) != 0:
        # If there are injuries on the page.
        injury_col_headers_html = tables[0].thead.find_all("th")
        injury_data_html = tables[0].tbody.find_all("tr")

        # Getting Injury Table headers.
        injury_col_headers = []
        for injury_col in injury_col_headers_html:
            injury_col_headers.append(injury_col.get_text())

        # Getting Injury Table data.
        injury_table_data = []
        for injury_row in injury_data_html:
            injury_row_data = []

            # Player name is in the "a" tag, first we have to find that.
            injury_row_data.append(injury_row.find("a").get_text())

            # Then we can drill down the other table data.
            r_inj_data = injury_row.find_all("td")
            for ird in r_inj_data:
                injury_row_data.append(ird.get_text())

            injury_table_data.append(injury_row_data)

        injury_data = {"headers": injury_col_headers, "row_data": injury_table_data}

    # If there are no injuries in the team.
    else:
        injury_data = {
            "headers": ["No injuries reported..."],
            "row_data": ["No injuries reported..."],
        }

    data = {"headers": col_headers, "row_data": table_data}

    # Next games, Coaches and Executives, Team Logos parsing.
    # Next Games
    next_game_text = soup.find(text="Next Game:").parent.parent
    next_game_parsed = [child.get_text().strip() for child in next_game_text.children]
    next_game = "".join(next_game_parsed[2].split(" ")).replace("\n", " ")

    # Team Coach
    coach_text = soup.find(text="Coach:").parent.parent
    coach_parsed = [child1 for child1 in coach_text.children]
    coach_link = f'https://www.basketball-reference.com{coach_parsed[2]["href"]}'
    coach = coach_parsed[2].get_text()

    # Team executive
    executive_text = soup.find(text="Executive:").parent.parent
    executive_parsed = [child1 for child1 in executive_text.children]
    executive_link = (
        f'https://www.basketball-reference.com{executive_parsed[2]["href"]}'
    )
    executive = executive_parsed[2].get_text()

    # Team Logo
    team_logo = soup.find("img", {"class": "teamlogo"})["src"]

    # Collating Next Game, Coach and Executive in one dictionary.
    extra_info = {
        "next_game": next_game,
        "coach": coach,
        "coach_link": coach_link,
        "executive": executive,
        "executive_link": executive_link,
        "team_logo": team_logo,
    }

    return data, injury_data, extra_info


def scrape_hooper_highlights(date):
    f = open("/home/csabimvp/mywebsite/config.json")
    config = json.load(f)

    bb_date = datetime.strptime(date, "%b %d, %Y")
    # today = datetime.today()
    # yesterday = today - timedelta(days=1)

    youtube = build("youtube", "v3", developerKey=config["YOUTUBE_API_KEY"])
    # channel_id = 'UC6yGoFvjKmRAlBfglOxNCGQ'
    playlist_id = "UU6yGoFvjKmRAlBfglOxNCGQ"

    r = (
        youtube.playlistItems()
        .list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=20,
        )
        .execute()
    )

    data = []

    for item in r["items"]:
        video_data = {}
        published = item["snippet"]["publishedAt"]
        published_obj = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")

        if published_obj > bb_date:
            title = item["snippet"]["title"]
            # thumbnail = item['snippet']['thumbnails']['high']['url']
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            video_data["title"] = title
            video_data["published"] = published
            # video_data['thumbnail'] = thumbnail
            video_data["video_id"] = video_id
            video_data["video_url"] = video_url

            data.append(video_data)

    return data


def scrape_motion_station(date):
    f = open("/home/csabimvp/mywebsite/config.json")
    config = json.load(f)

    bb_date = datetime.strptime(date, "%b %d, %Y")
    # today = datetime.today()
    # yesterday = today - timedelta(days=1)

    youtube = build("youtube", "v3", developerKey=config["YOUTUBE_API_KEY"])
    # channel_id = 'UC6yGoFvjKmRAlBfglOxNCGQ'
    playlist_id = "UULd4dSmXdrJykO_hgOzbfPw"

    r = (
        youtube.playlistItems()
        .list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=20,
        )
        .execute()
    )

    data = []

    for item in r["items"]:
        video_data = {}
        published = item["snippet"]["publishedAt"]
        published_obj = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")

        if published_obj > bb_date:
            title = item["snippet"]["title"]
            # thumbnail = item['snippet']['thumbnails']['high']['url']
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            video_data["title"] = title
            video_data["published"] = published
            # video_data['thumbnail'] = thumbnail
            video_data["video_id"] = video_id
            video_data["video_url"] = video_url

            data.append(video_data)

    return data


def scrape_team_logo(team):
    url = f"https://www.basketball-reference.com/teams/{team}/2024.html"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    # Team Logo
    team_logo = soup.find("img", {"class": "teamlogo"})["src"]

    return team_logo
