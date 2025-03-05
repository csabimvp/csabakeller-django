import json
import requests
from datetime import datetime, timedelta


class Token:
    def loadJson(name, path):
        jsonFile = json.load(open(path, "r"))
        return jsonFile[name]

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.keys = Token.loadJson(self.name, self.path)

    def getClientId(self):
        return self.keys["CLIENT_ID"]

    def getAccessToken(self):
        return self.keys["ACCESS_TOKEN"]

    def getAthleteId(self):
        return self.keys["ATHLETE_ID"]

    def isTokenExpired(self):
        today = datetime.now()
        expiryDate = datetime.strptime(self.keys["EXPIRY_DATE"], "%Y-%m-%d %H:%M:%S")
        if expiryDate < today:
            print("Token expired.")
            return True

    def refreshToken(self):
        today = datetime.now()
        data = {
            "grant_type": "refresh_token",
            "client_id": self.keys["CLIENT_ID"],
            "client_secret": self.keys["CLIENT_SECRET"],
            "refresh_token": self.keys["REFRESH_TOKEN"],
        }
        r = requests.post(self.keys["URL"], data=data).json()

        self.keys["ACCESS_TOKEN"] = r["access_token"]
        try:
            self.keys["SCOPE"] = r["scope"]
        except KeyError:
            pass

        # Save new Expiry Date
        expires_in = r["expires_in"]
        new_expiry_date = today + timedelta(seconds=expires_in)

        self.keys["EXPIRY_DATE"] = new_expiry_date.strftime("%Y-%m-%d %H:%M:%S")

        with open(self.path, "r+") as jsonFile:
            data = json.load(jsonFile)
            data[self.name] = self.keys
            jsonFile.seek(0)
            json.dump(data, jsonFile, indent=4, sort_keys=True)
            jsonFile.truncate()

        return print("Token refreshed.")


class Spotify(Token):
    def __init__(self, name, CREDENTIALS):
        super().__init__(name, CREDENTIALS)
        if super().isTokenExpired() == True:
            super().refreshToken()
        self.clientId = super().getClientId()
        self.accessToken = super().getAccessToken()
        self.userId = "11152365652"
        self.headers = {
            "Authorization": f"Bearer {self.accessToken}",
            "Content-Type": "application/json",
        }

    def __str__(self):
        return f"{self.clientId}"

    def getUserProfile(self):
        url = f"https://api.spotify.com/v1/users/{self.userId}"
        r = requests.get(url, headers=self.headers).json()
        return r

    def getTopArtists(self, mytype="artists", limit=5):
        url = f"https://api.spotify.com/v1/me/top/{mytype}?time_range=medium_term&limit={limit}"
        r = requests.get(url, headers=self.headers).json()

        content = []

        for item in r["items"]:
            data = {}
            data["id"] = item["id"]
            data["name"] = item["name"]
            data["genres"] = item["genres"]
            data["image"] = item["images"][0]["url"]
            content.append(data)

        return content

    def getTopTracks(self, mytype="tracks", limit=5):
        url = f"https://api.spotify.com/v1/me/top/{mytype}?time_range=medium_term&limit={limit}"
        r = requests.get(url, headers=self.headers).json()

        content = []

        for item in r["items"]:
            data = {}
            data["id"] = item["id"]
            data["artist"] = item["artists"][0]["name"]
            data["album"] = item["album"]["name"]
            data["name"] = item["name"]
            data["release_date"] = item["album"]["release_date"]
            data["total_tracks"] = item["album"]["total_tracks"]
            data["album_image"] = item["album"]["images"][0]["url"]
            data["track_url"] = item["external_urls"]["spotify"]
            content.append(data)

        return content


class Strava(Token):
    def __init__(self, name, CREDENTIALS):
        super().__init__(name, CREDENTIALS)
        if super().isTokenExpired() == True:
            super().refreshToken()
        self.accessToken = super().getAccessToken()
        self.athleteId = super().getAthleteId()
        self.headers = {
            "Authorization": f"Bearer {self.accessToken}",
            "Content-Type": "application/json",
        }

    def __str__(self):
        return f"{self.athleteId}"

    def getAthleteStats(self):
        url = f"https://www.strava.com/api/v3/athletes/{self.athleteId}/stats"
        r = requests.get(url, headers=self.headers).json()

        data = dict()
        data["recent_ride_totals"] = r["recent_ride_totals"]
        data["all_ride_totals"] = r["all_ride_totals"]
        data["ytd_ride_totals"] = r["ytd_ride_totals"]
        data["recent_run_totals"] = r["recent_run_totals"]
        data["all_run_totals"] = r["all_run_totals"]
        data["ytd_run_totals"] = r["ytd_run_totals"]
        # data["recent_swim_totals"] = r["recent_swim_totals"]
        # data["all_swim_totals"] = r["all_swim_totals"]
        # data["ytd_swim_totals"] = r["ytd_swim_totals"]

        return data

    def getAthleteActivities(self):
        url = f"https://www.strava.com/api/v3/activities"
        r = requests.get(url, headers=self.headers).json()

        data = list()
        for item in r:
            content = dict()
            content["id"] = item["id"]
            content["sport_type"] = item["sport_type"]
            content["distance"] = item["distance"]
            content["elapsed_time"] = item["elapsed_time"]
            content["activityUrl"] = f"https://www.strava.com/activities/{item['id']}"
            data.append(content)
        return data
