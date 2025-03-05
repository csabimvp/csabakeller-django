# Django and Rest Framework imports.
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import generics
from django_filters import rest_framework as filters


# Local imports
from .serializers import AccountSerializer
from .functions import generate_password
from .models import Account, EncryptionToken


class GeneratePasswordView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]

    # Exclude this view from API authentication.
    authentication_classes = []
    permission_classes = []

    #/api/passwords/generate/?password_length=10&special_characters=True
    def get(self, request):
        password_length = int(self.request.query_params.get("password_length"))
        special_characters = self.request.query_params.get("special_characters")
        password = generate_password(password_length, special_characters)
        content = {"password": password, "password_length": password_length, "special_characters": special_characters}
        return Response(content)


class GetEncryptionToken(generics.ListAPIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        username = self.request.query_params.get("username")
        tokens = EncryptionToken.objects.filter(user__username=username).values()[0]
        content = {"token": tokens["token"], "id": tokens["id"]}
        return Response(content)


# Custom filter for filtering Payments by Month and Year
class AccountFilter(filters.FilterSet):
    class Meta:
        model = Account
        fields = ["user", "id", "name", "account_name"]


class AccountsView(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AccountFilter