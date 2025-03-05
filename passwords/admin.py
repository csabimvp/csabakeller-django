from django.contrib import admin
from .models import EncryptionToken, Account


@admin.register(EncryptionToken)
class EncryptionTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "token"]
    list_filter = ["user"]

    class Meta:
        model = EncryptionToken


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "user",
        "account_name",
        "url",
        "memorable",
        "security_question",
        "created",
        "updated",
    ]
    list_filter = ["user", "name"]

    class Meta:
        model = Account