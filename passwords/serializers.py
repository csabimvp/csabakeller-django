from rest_framework import serializers
from .models import Account
from .functions import decrypt_text


class AccountSerializer(serializers.ModelSerializer):
    decrypted_password = serializers.SerializerMethodField("decrypt_pw_serializer")
    decrypted_account_name = serializers.SerializerMethodField(
        "decrypt_account_serializer"
    )

    # SerializerMethodField
    def decrypt_pw_serializer(self, item):
        return decrypt_text(item.key, item.password)

    # SerializerMethodField
    def decrypt_account_serializer(self, item):
        return decrypt_text(item.key, item.account_name)

    class Meta:
        model = Account
        fields = [
            "user",
            "id",
            "key",
            "name",
            "password",
            "account_name",
            "decrypted_account_name",
            "decrypted_password",
            "url",
            "memorable",
            "security_question",
            "created",
            "updated",
        ]
