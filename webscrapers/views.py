import re
import json
import os
from pathlib import Path
from datetime import timedelta

# Django and Rest Framework imports.
from django.http.response import JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import generics

# Local imports
from .scrapers import (
    nba_scoreboard_scraper,
    nba_stats_daily_leaders_scraper,
    nba_standings_scraper,
    team_contracts,
    team_player_stats,
    scrape_hooper_highlights,
    scrape_motion_station,
    # scrape_team_logo
)

from .analytics import (
    # annual_team_analysis,
    season_leaders_table,
)

BASE_DIR = Path(__file__).resolve().parent.parent
WEBSCRAPERS_DIR = os.path.join(BASE_DIR, "webscrapers")

f = open(os.path.join(WEBSCRAPERS_DIR, "assets", "nba_teams.json"))
teams = json.load(f)

# custom API view for web scraped NBA stats data


class NbaStatsView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]

    # Exclude this view from API authentication.
    authentication_classes = []
    permission_classes = []

    # Creating get function for GET request.
    def get(self, request):
        url1 = "https://www.basketball-reference.com/boxscores/"
        url2 = "https://stats.nba.com/js/data/widgets/home_daily.json"
        url3 = "https://www.basketball-reference.com/"

        # Scrape the webs.
        games_data, date = nba_scoreboard_scraper(url1)
        # hooper_highlights = scrape_hooper_highlights(date)
        motions_highlights = scrape_motion_station(date)
        player_stats = nba_stats_daily_leaders_scraper(url2)
        nba_standings = nba_standings_scraper(url3)

        # if len(games_data) == len(hooper_highlights):
        for game in games_data:
            winner = game["winner_team"]
            loser = game["loser_team"]

            game["winner_logo"] = teams[winner][3]
            game["loser_logo"] = teams[loser][3]

            game["winner_long_name"] = teams[winner][1]
            game["loser_long_name"] = teams[loser][1]

            # for hooper_highlight in hooper_highlights:
            #     hooper_title = hooper_highlight["title"]

            #     if re.search(winner, hooper_title) and re.search(loser, hooper_title):
            #         game["hooper_video_id"] = hooper_highlight["video_id"]

            for motion_highlight in motions_highlights:
                motion_title = motion_highlight["title"]

                if re.search(teams[winner][0], motion_title) and re.search(
                    teams[loser][0], motion_title
                ):
                    game["motion_video_id"] = motion_highlight["video_id"]
                    # game['thumbnail'] = motion_highlight['thumbnail']

        content = {
            "date": date,
            "games_data": games_data,
            "player_stats": player_stats,
            "nba_standings": nba_standings,
        }

        return Response(content)


class NbaTeamContractsAndStatsView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]

    # Exclude this view from API authentication.
    authentication_classes = []
    permission_classes = []

    # Creating get function for GET request.
    def get(self, request):

        # Getting team name from URL --- /?team=""
        team_name = self.request.query_params.get("team")

        team_salaries = team_contracts(team_name)
        team_page_scraper_results = team_player_stats(team_name)
        team_player_statistics = team_page_scraper_results[0]
        team_injuries = team_page_scraper_results[1]
        extra_info = team_page_scraper_results[2]
        # team_analytics = annual_team_analysis(team_name)

        content = {
            "salaries": team_salaries,
            "team_stats": team_player_statistics,
            "team_injuries": team_injuries,
            # "team_analytics": team_analytics,
            "extra_info": extra_info,
        }

        return Response(content)


class SeasonBoxScoreLeaders(generics.ListAPIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        content = season_leaders_table()

        return Response(content)


class Authenticate(generics.ListAPIView):
    renderer_classes = [JSONRenderer]

    # Exclude this view from API authentication.
    authentication_classes = []
    permission_classes = []

    # Creating get function for GET request.
    def get(self, request):

        # Getting items from the url
        code = self.request.query_params.get("code")
        state = self.request.query_params.get("state")

        if code:
            content = {"code": code, "state": state}
        else:
            content = {"name": "John Doe"}

        return Response(content)


class StravaAthleteStatsView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]

    # Exclude this view from API authentication.
    authentication_classes = []
    permission_classes = []

    # Creating get function for GET request.
    def get(self, request):
        # Load Strava data from json file.
        f = open("/home/csabimvp/mywebsite/webscrapers/activities.json")
        activities = json.load(f)

        # Load Strava data from json file.
        f = open("/home/csabimvp/mywebsite/webscrapers/strava_stats.json")
        strava_stats = json.load(f)

        mystats = {}
        mystats["all_ride_totals"] = {}
        mystats["all_run_totals"] = {}
        mystats["ytd_ride_totals"] = {}
        mystats["ytd_run_totals"] = {}

        mystats["all_ride_totals"]["count"] = strava_stats["all_ride_totals"]["count"]
        mystats["all_ride_totals"]["distance"] = strava_stats["all_ride_totals"][
            "distance"
        ]
        mystats["all_ride_totals"]["elevation_gain"] = strava_stats["all_ride_totals"][
            "elevation_gain"
        ]
        mystats["all_ride_totals"]["moving_time"] = str(
            timedelta(seconds=int(strava_stats["all_ride_totals"]["moving_time"]))
        )
        mystats["all_ride_totals"]["time"] = int(
            strava_stats["all_ride_totals"]["moving_time"]
        )

        mystats["all_run_totals"]["count"] = strava_stats["all_run_totals"]["count"]
        mystats["all_run_totals"]["distance"] = strava_stats["all_run_totals"][
            "distance"
        ]
        mystats["all_run_totals"]["elevation_gain"] = strava_stats["all_run_totals"][
            "elevation_gain"
        ]
        mystats["all_run_totals"]["moving_time"] = str(
            timedelta(seconds=int(strava_stats["all_run_totals"]["moving_time"]))
        )
        mystats["all_run_totals"]["time"] = int(
            strava_stats["all_run_totals"]["moving_time"]
        )

        mystats["ytd_ride_totals"]["count"] = strava_stats["ytd_ride_totals"]["count"]
        mystats["ytd_ride_totals"]["distance"] = strava_stats["ytd_ride_totals"][
            "distance"
        ]
        mystats["ytd_ride_totals"]["elevation_gain"] = strava_stats["ytd_ride_totals"][
            "elevation_gain"
        ]
        mystats["ytd_ride_totals"]["moving_time"] = str(
            timedelta(seconds=int(strava_stats["ytd_ride_totals"]["moving_time"]))
        )
        mystats["ytd_ride_totals"]["time"] = int(
            strava_stats["ytd_ride_totals"]["moving_time"]
        )

        mystats["ytd_run_totals"]["count"] = strava_stats["ytd_run_totals"]["count"]
        mystats["ytd_run_totals"]["distance"] = strava_stats["ytd_run_totals"][
            "distance"
        ]
        mystats["ytd_run_totals"]["elevation_gain"] = strava_stats["ytd_run_totals"][
            "elevation_gain"
        ]
        mystats["ytd_run_totals"]["moving_time"] = str(
            timedelta(seconds=int(strava_stats["ytd_run_totals"]["moving_time"]))
        )
        mystats["ytd_run_totals"]["time"] = int(
            strava_stats["ytd_run_totals"]["moving_time"]
        )

        myacitivities = []
        for activity in activities[:3]:
            data = {}
            data["id"] = activity["id"]
            data["distance"] = activity["distance"]
            data["elapsed_time"] = str(timedelta(seconds=int(activity["elapsed_time"])))
            data["name"] = activity["name"]
            data["sport_type"] = activity["sport_type"]
            data["start_date"] = activity["start_date"]
            data["total_elevation_gain"] = activity["total_elevation_gain"]
            myacitivities.append(data)

        content = {"stats": mystats, "activities": myacitivities}

        return Response(content)
