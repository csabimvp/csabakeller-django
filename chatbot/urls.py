from django.urls import path
from django.conf.urls import include
from .views import ChatbotQuestionView, ChatbotRequestsView
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r"chatbotrequests", ChatbotRequestsView)


app_name = "chatbot"

urlpatterns = [
    path("v1/", ChatbotQuestionView.as_view()),
    path("", include(router.urls)),
]
