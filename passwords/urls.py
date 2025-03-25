from django.urls import include, path
from django.conf.urls import include
from rest_framework import routers
from .views import GeneratePasswordView, AccountsView, GetEncryptionToken, CustomLoginView


router = routers.SimpleRouter()
router.register(r"accounts", AccountsView)


app_name = "passwords"


urlpatterns = [
    path("generate/", GeneratePasswordView.as_view()),
    path("encryption_tokens/", GetEncryptionToken.as_view()),
    path("customlogin/", CustomLoginView.as_view()),
    path("", include(router.urls)),
]
