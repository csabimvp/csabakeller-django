import random
import string
from cryptography.fernet import Fernet


def generate_password(password_length=30, special_characters="False"):
    if special_characters == "True":
        characterList = string.ascii_letters + string.digits + string.punctuation
    else:
        characterList = string.ascii_letters + string.digits

    password = "".join([random.choice(characterList) for i in range(password_length)])
    return password


def encrypt_text(key, text):
    token = Fernet(str(key).encode("utf-8")).encrypt(text.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_text(key, text):
    password = Fernet(str(key).encode("utf-8")).decrypt(text)
    return password.decode("utf-8")


def generate_key():
    return Fernet.generate_key().decode("utf-8")