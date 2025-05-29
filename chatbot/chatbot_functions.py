import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import psycopg2
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent.parent

config = json.load(open(os.path.join(BASE_DIR, "config.json")))
nba_teams = json.load(
    open(os.path.join(BASE_DIR, "chatbot", "assets", "nba_teams.json"))
)


def WhatsTheTime():
    today = datetime.now().strftime("%A, %H:%M:%S")
    today = f"{today} GMT"
    return today


def WhatsTheDate():
    today = datetime.now().strftime("%A, %d-%m-%Y")
    return today


def GetWeatherData(variables):
    # Converting Variables list elemtents to one string.
    if len(variables) == 2:
        city = " ".join(variables)
    elif len(variables) == 1:
        city = variables[0]
    else:
        city = "london"

    API_KEY = config["WEATHER_API_KEY"]
    API_URL = "https://api.openweathermap.org/data/2.5/"

    url = f"{API_URL}weather?q={city}&units=metric&&appid={API_KEY}"

    # pinging the API
    r = requests.get(url)

    # Handle not existing cities, or some other errors.
    if r.status_code != 200:
        content = "Oops, couldn't find that..."
    # If City was found.
    else:
        response = r.json()

        # Getting data from Requests response.
        temperature = f'{round(response["main"]["temp"])}°C'
        location = f'{response["name"]}, {response["sys"]["country"]}'
        sunrise = datetime.fromtimestamp(response["sys"]["sunrise"]).strftime(
            "%H:%M:%S"
        )
        sunset = datetime.fromtimestamp(response["sys"]["sunset"]).strftime("%H:%M:%S")
        weather = response["weather"][0]["main"]
        temp_min = f'{round(response["main"]["temp_min"])}°C'
        temp_max = f'{round(response["main"]["temp_max"])}°C'
        feels_like = f'{round(response["main"]["feels_like"])}°C'
        wind = f'{response["wind"]["speed"]} m/s'

        # Return content
        content = {
            "temperature": temperature,
            "location": location,
            "weather": weather,
            "sunrise": sunrise,
            "sunset": sunset,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "feels_like": feels_like,
            "wind": wind,
        }

    return content


def find_nba_team(team_name):
    for team in nba_teams.keys():
        if team_name in nba_teams[team]:
            content = {"team": team, "team_name": max(nba_teams[team], key=len)}
            return content
        else:
            pass


def GetNBATeamInfo(variables):
    # print(variables)
    # Converting Variables list elemtents to one string.
    if len(variables) > 1:
        team_to_search = " ".join(variables)
        result = find_nba_team(team_to_search)
        if result:
            team = result["team"]
            team_name = result["team_name"]
        else:
            team = None
            team_name = None
    elif len(variables) == 1:
        team_to_search = variables[0]
        result = find_nba_team(team_to_search)
        if result:
            team = result["team"]
            team_name = result["team_name"]
        else:
            team = None
            team_name = None
    else:
        team = "MIA"
        team_name = "Miami Heat"

    try:
        url = f"https://www.basketball-reference.com/teams/{team}/2024.html"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")

        info_section = soup.find("div", {"id": "info"}).find_all("p")
        record_parsed = [child.get_text().strip() for child in info_section[2].children]
        record_stats = record_parsed[2].split(", ")
        record1 = record_stats[0]
        record2 = record_stats[1] + " " + " ".join(record_parsed[3:5])
        record = f"{record1} -- {record2}"

        next_game_parsed = [
            child.get_text().strip() for child in info_section[4].children
        ]
        next_game = "".join(next_game_parsed[2].split(" ")).replace("\n", " ")

        coach_text = soup.find(text="Coach:").parent.parent
        coach_parsed = [child1.get_text() for child1 in coach_text.children]
        coach = "".join(coach_parsed[2:])

        # Getting thumbnail picture
        thumbnail = soup.find("div", {"id": "info"}).find("img")["src"]

        content = {
            "team_name": team_name,
            "record": record,
            "next_game": next_game,
            "coach": coach,
            "url": url,
            "thumbnail": thumbnail,
            "error": False,
        }
    except AttributeError:
        content = {"error": True}

    return content


def GetTVShowInfo(tv_show):
    # Converting Variables list elemtents to one string.
    url = "-".join(
        [char.lower() for char in [show.replace(":", "") for show in tv_show]]
    )

    r = requests.get(f"https://next-episode.net/{url}")
    soup = BeautifulSoup(r.content, "html.parser")

    # Try / Except if the question doesn't have the Full and Right TV show name...
    try:
        show_name = soup.find("div", {"id": "show_name"}).get_text()
        info_section = soup.find("div", {"id": "middle_section"}).find_all("div")

        genres = info_section[1].find_all("a")
        genres_parsed = [item.get_text() for item in genres]

        streams = info_section[5].find_all("a")
        streams_parsed = [item.get_text() for item in streams]
        created = info_section[13].find_all("a")
        created_parsed = [
            # [item.get_text(), f'https:{item["href"]}'] for item in created
            item.get_text()
            for item in created
        ]

        # Getting thumbnail picture
        thumbnail = (
            f'{soup.find("div", {"id": "big_image_container"}).find("img")["src"]}'
        )

        # Getting IMDb link
        info_section2 = soup.find("div", {"id": "middle_section"}).find_all("a")
        imdb = [
            item["href"] for item in info_section2 if "imdb" in item.get_text().lower()
        ]

        # Getting Cast members
        cast_section = soup.find("div", {"id": "middle_section_similar"}).find_all(
            "div", {"class": "castitem"}
        )

        castMembers = list()
        for cast in cast_section:
            castMember = dict()
            castMember["name"] = " ".join(
                [name.get_text() for name in cast.find_all("h3")]
            )
            castMember["character"] = " ".join(
                [name.get_text() for name in cast.find_all("div")]
            )
            castMember["link"] = f'https://next-episode.net{cast.find("a")["href"]}'
            castMember["thumbnail"] = cast.find("img")["src"]
            castMembers.append(castMember)

        try:
            previous_episode = soup.find("div", {"id": "previous_episode"})
            previous_episode_texts = (
                previous_episode.get_text().replace("\t", "").split("\n")
            )
            clean = [
                (item.split(":")[0].lower(), item.split(":")[1])
                for item in previous_episode_texts
                if len(item) > 1 and ":" in item
            ]

            next_episode = (
                soup.find("div", {"id": "next_episode"})
                .get_text()
                .replace("\t", "")
                .split("\n")
            )
            next_episode_clean = [
                elem.strip()
                for elem in next_episode
                if len(elem.strip()) > 1 and elem != "Next Episode"
            ]

            # Creating database
            data = {k: v for (k, v) in clean}
            # data["url"] = url
            data["thumbnail"] = thumbnail
            data["imdb"] = imdb[0]
            data["show_name"] = show_name
            data["genre"] = genres_parsed
            data["streams"] = streams_parsed
            data["created"] = created_parsed
            data["cast"] = castMembers

            if len(clean) + 1 == len(next_episode_clean):
                # content = {}
                data["running"] = True
                next_episode_clean2 = [
                    (item.split(":")[0].lower(), item.split(":")[1])
                    for item in next_episode_clean
                    if len(item) > 1 and ":" in item
                ]
                data2 = {x: z for (x, z) in next_episode_clean2}
                # content["details"] = data2
                data["next_episode_name"] = data2["name"]
                data["next_episode_countdown"] = data2["countdown"]
                data["next_episode_date"] = data2["date"]
                data["next_episode_season"] = data2["season"]
                data["next_episode_episode"] = data2["episode"]
                # data["next_episode_summary"] = data2["summary"]
            else:
                # content = {}
                data["running"] = False
                data["next_episode_name"] = next_episode_clean

        except AttributeError:
            data = dict()
            data["thumbnail"] = thumbnail
            data["imdb"] = imdb[0]
            data["show_name"] = show_name
            data["genre"] = genres_parsed
            data["streams"] = streams_parsed
            data["created"] = created_parsed
            data["cast"] = castMembers
            data["running"] = False

    except AttributeError:
        data = {"error": True}

    return data


def GetNASAapod():
    KEY = config["NASA_API_KEY"]
    URL = f"https://api.nasa.gov/planetary/apod?api_key={KEY}"

    response = requests.get(url=URL).json()
    return response


def GetJsonData(key):
    if key == "CONTACT":
        data = {
            "facebook": "https://www.facebook.com/kellercsabii/",
            "instagram": "https://www.instagram.com/kellercsabii/",
            "linkedin": "https://www.linkedin.com/in/csaba-keller-57600a126/",
            "github": "https://github.com/csabimvp",
            "email": "kellercsabii@gmail.com",
        }
        return data
    else:
        data = json.load(
            open(r"/home/csabimvp/mywebsite/webscrapers/StravaSpotfiy.json")
        )
        return data[key]


def GetNBAStandings():
    r = requests.get("https://www.basketball-reference.com/")
    soup = BeautifulSoup(r.content, "html.parser")

    # Scraping Eastern and Western conference tables.
    eastern_conf_table = soup.find("table", id="confs_standings_E")
    western_conf_table = soup.find("table", id="confs_standings_W")

    eastern_rows = eastern_conf_table.find_all("tr")
    eastern_rows.pop(0)
    western_rows = western_conf_table.find_all("tr")
    western_rows.pop(0)

    # Creating dictionary to store data.
    nba_standings = {"eastern_conference": [], "western_conference": []}

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

        eastern_df["team_name"] = max(nba_teams[team_name], key=len)
        eastern_df["wins"] = wins
        eastern_df["losses"] = losses
        eastern_df["games_played"] = games_played
        eastern_df["pct"] = pct

        nba_standings["eastern_conference"].append(eastern_df)

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

        western_df["team_name"] = max(nba_teams[team_name], key=len)
        western_df["wins"] = wins
        western_df["losses"] = losses
        western_df["games_played"] = games_played
        western_df["pct"] = pct

        nba_standings["western_conference"].append(western_df)

    return nba_standings


def YouTubeSearch(query):
    youtube = build("youtube", "v3", developerKey=config["YOUTUBE_API_KEY"])
    r = youtube.search().list(part="snippet", q=query, maxResults=5).execute()
    return r["items"]


def StravaExtractDataFromSQL():
    # Postgres Database Connection
    conn = psycopg2.connect(
        # "host=192.168.0.86 user=csabimvp password= dbname=strava"
        f"host=localhost user={config["POSTGRES"]["USER"]} password={config["POSTGRES"]["PASSWORD"]} dbname=utilities"
    )

    with conn.cursor() as cursor:
        ### Activities
        # Schema Query
        activities_schema_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='strava' AND TABLE_NAME='athlete_activities';"
        cursor.execute(activities_schema_query)
        activities_schema = [s[0] for s in cursor]
        # Data Query
        activities_data_query = (
            f"SELECT * FROM strava.athlete_activities ORDER BY start_date DESC LIMIT 5;"
        )
        cursor.execute(activities_data_query)
        activities_data = cursor.fetchall()
        activities_container = [
            {activities_schema[i]: item[i] for i in range(len(activities_schema))}
            for item in activities_data
        ]
        cleaned_container = [
            {
                k: elem[k]
                for k in (
                    "activity_id",
                    "distance",
                    "moving_time",
                    "kudos_count",
                    "pr_count",
                    "achievement_count",
                    "sport_type",
                    "start_date",
                )
            }
            for elem in activities_container
        ]

        ### Stats
        # Schema Query
        stats_schema_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='strava' AND TABLE_NAME='athlete_stats';"
        cursor.execute(stats_schema_query)
        stats_schema = [s[0] for s in cursor]
        # Data Query
        data_query = f"SELECT * FROM strava.athlete_stats WHERE sport_type = 'running' AND stat_type IN ('all_time', 'year_to_date');"
        cursor.execute(data_query)
        stats_data = cursor.fetchall()
        container = [
            {stats_schema[i]: item[i] for i in range(len(stats_schema))}
            for item in stats_data
        ]

        # API Response
        response = {}
        response["activites"] = cleaned_container
        response["stats"] = container
    return response


def SpotifyExtractDataFromSQL():
    # Postgres Database Connection
    conn = psycopg2.connect("host=192.168.0.86 user=csabimvp password= dbname=spotify")

    with conn.cursor() as cursor:
        ### Activities
        # Schema Query
        activities_schema_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='strava' AND TABLE_NAME='athlete_activities';"
        cursor.execute(activities_schema_query)
        activities_schema = [s[0] for s in cursor]
        # Data Query
        activities_data_query = (
            f"SELECT * FROM strava.athlete_activities ORDER BY start_date DESC LIMIT 5;"
        )
        cursor.execute(activities_data_query)
        activities_data = cursor.fetchall()
        activities_container = [
            {activities_schema[i]: item[i] for i in range(len(activities_schema))}
            for item in activities_data
        ]
        cleaned_container = [
            {
                k: elem[k]
                for k in (
                    "activity_id",
                    "distance",
                    "moving_time",
                    "kudos_count",
                    "pr_count",
                    "achievement_count",
                    "sport_type",
                    "start_date",
                )
            }
            for elem in activities_container
        ]

        ### Stats
        # Schema Query
        stats_schema_query = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='strava' AND TABLE_NAME='athlete_stats';"
        cursor.execute(stats_schema_query)
        stats_schema = [s[0] for s in cursor]
        # Data Query
        data_query = f"SELECT * FROM strava.athlete_stats WHERE sport_type = 'running' AND stat_type IN ('all_time', 'year_to_date');"
        cursor.execute(data_query)
        stats_data = cursor.fetchall()
        container = [
            {stats_schema[i]: item[i] for i in range(len(stats_schema))}
            for item in stats_data
        ]

        # API Response
        response = {}
        response["activites"] = cleaned_container
        response["stats"] = container
    return response


if __name__ == "__main__":
    response = StravaExtractDataFromSQL()
    print(response)
