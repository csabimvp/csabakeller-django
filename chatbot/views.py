# Django and Rest Framework imports.
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import generics, viewsets


# Local imports
from .chatbot import handle_question
from .models import ChatbotRequest
from .serializers import ChatbotRequestSerializer


# Chatbot API
class ChatbotQuestionView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]

    # Exclude this view from API authentication.
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        # Getting question from URL --- /?query=""
        question = self.request.query_params.get("query")
        # Replace the url %20 to spaces
        # question = question.replace("%20", " ")

        content = handle_question(question)

        # Save Requests Data into database...
        # requestData = dict()
        # requestData["query"] = self.request.query_params.get("query")
        # requestData["intent"] = content["intent"]
        # requestData["confidence"] = content["confidence"]
        # requestData["remote_address"] = request.META["REMOTE_ADDR"]
        # requestData["user_agent"] = request.META["HTTP_USER_AGENT"]
        # dontSave = ("Greetings", "Hello")
        # if (requestData["intent"], requestData["query"]) != dontSave:
        #     ChatbotRequest.create_from_request(requestData)

        return Response(content)


class ChatbotRequestsView(viewsets.ModelViewSet):
    queryset = ChatbotRequest.objects.all()
    serializer_class = ChatbotRequestSerializer
