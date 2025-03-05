from django.urls import path
from .views import (
    NbaStatsView,
    NbaTeamContractsAndStatsView,
    SeasonBoxScoreLeaders,
    Authenticate,
    StravaAthleteStatsView,
)

app_name = "nbastats"

urlpatterns = [
    path("authenticate/", Authenticate.as_view()),
    path("stravastats/", StravaAthleteStatsView.as_view()),
    path("nbastats/", NbaStatsView.as_view()),
    path("teams/", NbaTeamContractsAndStatsView.as_view()),
    path("leaders/", SeasonBoxScoreLeaders.as_view()),
]
