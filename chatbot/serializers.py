from rest_framework import serializers
from .models import ChatbotRequest


class ChatbotRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotRequest
        fields = "__all__"
