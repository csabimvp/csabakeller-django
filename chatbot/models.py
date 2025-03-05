from django.db import models


# Create your models here.
class ChatbotRequest(models.Model):
    query = models.CharField(max_length=300)
    intent = models.CharField(max_length=250)
    confidence = models.FloatField()
    remote_address = models.CharField(max_length=250)
    user_agent = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("intent",)
        verbose_name = "Chatbot Requests"
        verbose_name_plural = "Chatbot Requests"

    def __str__(self):
        return self.intent

    @classmethod
    def create_from_request(cls, req):
        chatbotRequest = cls(
            query=req["query"],
            intent=req["intent"],
            confidence=req["confidence"],
            remote_address=req["remote_address"],
            user_agent=req["user_agent"],
        )
        chatbotRequest.save()
        return chatbotRequest
