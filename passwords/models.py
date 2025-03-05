from django.db import models
from django.conf import settings
from .functions import encrypt_text, generate_key


class EncryptionToken(models.Model):
    def token_default():
        return generate_key()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=250, unique=True, default=token_default)
    token_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("user",)
        verbose_name = "Encryption Token"
        verbose_name_plural = "Encryption Tokens"

    def __str__(self):
        return self.token

    def get_token(self):
        return self.token


#class AccountCategory(models.Model):
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    name = models.CharField(max_length=100, db_index=True)

#    class Meta:
#        ordering = ("name",)
#        verbose_name = "Account Categories"
#        verbose_name_plural = "Account Categories"

#    def __str__(self):
#        return self.name


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.ForeignKey(EncryptionToken, on_delete=models.CASCADE)
    #category = models.ForeignKey(AccountCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, db_index=True)
    account_name = models.CharField(max_length=250)
    password = models.CharField(max_length=250, blank=True)
    url = models.CharField(max_length=250, blank=True)
    memorable = models.CharField(max_length=250, blank=True)
    security_question = models.CharField(max_length=250, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Accounts"
        verbose_name_plural = "Accounts"

    def __str__(self):
        return self.name

    # Override save method to encrypt password before adding it to the Database.
    def save(self, *args, **kwargs):
        self.account_name = encrypt_text(self.key, self.account_name)
        if self.password:
            self.password = encrypt_text(self.key, self.password)
        super(Account, self).save(*args, **kwargs)