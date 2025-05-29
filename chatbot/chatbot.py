# required modules
import json
import os
import pickle
import random
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
CHATBOT_DIR = os.path.join(BASE_DIR, "chatbot")

# import pandas as pd
import nltk
from tensorflow.keras.models import load_model

# from nltk.stem import WordNetLemmatizer


# Download NLTK documents.
# nltk.download('punkt', download_dir=os.path.join(CHATBOT_DIR, "nltk"))
# nltk.download('punkt_tab', download_dir=os.path.join(CHATBOT_DIR, "nltk"))
# nltk.download('wordnet', download_dir=os.path.join(CHATBOT_DIR, "nltk"))


# Changing the path to the NLTK tokenizers as per above. --- Have to keep this line of code in order to make it work.
nltk.data.path.append(os.path.join(CHATBOT_DIR, "nltk"))


# Import chatbot functions
from .chatbot_functions import (
    GetJsonData,
    GetNASAapod,
    GetNBAStandings,
    GetNBATeamInfo,
    GetTVShowInfo,
    GetWeatherData,
    StravaExtractDataFromSQL,
    WhatsTheDate,
    WhatsTheTime,
    YouTubeSearch,
)

# Global variables.
# lemmatizer = WordNetLemmatizer()
# assets_path = r"/home/csabimvp/mywebsite/chatbot/assets"
# saves_path = r"/home/csabimvp/mywebsite/chatbot/model"
IGNORE_LETTERS = ["?", "!", ".", ","]


# loading the files we made previously
intents = json.load(open(os.path.join(CHATBOT_DIR, "assets", "intents.json")))
words = pickle.load(
    open(os.path.join(CHATBOT_DIR, "model", "questions - words.pkl"), "rb")
)
classes = pickle.load(
    open(os.path.join(CHATBOT_DIR, "model", "questions - classes.pkl"), "rb")
)
model = load_model(os.path.join(CHATBOT_DIR, "model", "questions.h5"))


# Fucntion to Lemmatize the user's input.
def clean_up_sentences(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [
        word.lower() for word in sentence_words if word not in IGNORE_LETTERS
    ]
    # sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words if word not in ignore_letters]
    return sentence_words


# Function to Check if the words from the user's input are in the patterns JSON.
def bagw(sentence):
    # separate out words from the input sentence
    sentence_words = clean_up_sentences(sentence)

    # Words are in the Intents.json patterns
    bag = [0] * len(words)

    # Words couldn't match, probably variables for functions.
    variables = []
    # variables = [variable.lower() for variable in sentence_words if variable not in words]

    for w in sentence_words:
        variables.append(w.lower()) if w not in words else None
        for i, word in enumerate(words):
            # check whether the word is present in the input as well
            if word == w:
                # as the list of words created earlier.
                bag[i] = 1

    # return a numpy array
    return np.array(bag), variables


# Function to Predict user's intent.
def predict_class(sentence):
    bow, variable = bagw(sentence)
    res = model.predict(np.array([bow]))[0]
    # print(variable)

    ERROR_THRESHOLD = 0.85
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    return_list = []
    if len(results) > 0:
        results.sort(key=lambda x: x[1], reverse=True)
        # print(f"This is the results: {results}")
        for r in results:
            return_list.append(
                {"success": True, "intent": classes[r[0]], "probability": str(r[1])}
            )
            print(f"{return_list}")
    else:
        return_list.append({"success": False, "intent": "", "probability": 0})

    # Return response
    return return_list, variable


# Function to generate ChatBot response.
def get_response(intents_list, intents_json):
    tag = intents_list[0]["intent"]
    confidence = intents_list[0]["probability"]
    success = intents_list[0]["success"]
    intent = intents_json[tag]
    function_code = intent["functionCode"]

    # Give the Whole List as a response if the Intent is "PersonalProjects", otherwise give a random one.
    if tag != "PersonalProjects":
        response = random.choice(intent["responses"])
    else:
        response = intent["responses"]

    content = {
        "success": success,
        "intent": tag,
        "response": response,
        "function_code": function_code,
        "confidence": confidence,
    }
    return content


function_mappings = {
    "WhatsTheDate": WhatsTheDate,
    "WhatsTheTime": WhatsTheTime,
    "GetWeatherData": GetWeatherData,
    "GetNBATeamInfo": GetNBATeamInfo,
    "GetTVShowInfo": GetTVShowInfo,
    "StravaInfo": StravaExtractDataFromSQL,
    "SpotifyInfo": GetJsonData,
    "Contact": GetJsonData,
    "GetNASAapod": GetNASAapod,
    "GetNBAStandings": GetNBAStandings,
    "YouTubeSearch": YouTubeSearch,
}


def handle_question(question):
    # Exctracting Intents and Variables
    ints, variables = predict_class(question)

    # Content for response
    content = {}

    if ints[0]["success"]:
        res = get_response(ints, intents)
        intent = res["intent"]
        function_code = res["function_code"]
        response = res["response"]
        confidence = res["confidence"]
        success = res["success"]

        content["response"] = response
        content["intent"] = intent
        content["confidence"] = float(confidence)
        content["value"] = ""

        if len(function_code) > 0:
            if (
                intent == "Weather"
                or intent == "NBATeamInfo"
                or intent == "YouTubeSearch"
            ):
                value = function_mappings[function_code](variables)
                # print(value)
                content["value"] = value
            # Add "The" to the variable if the Question has it. To make sure there is a hit for the Request call.
            elif intent == "TVShowInfo":
                if "the" in question or "The" in question:
                    variables.insert(0, "the")
                    value = function_mappings[function_code](variables)
                else:
                    value = function_mappings[function_code](variables)
                content["value"] = value
            # Strava
            elif intent == "StravaInfo":
                value = GetJsonData("STRAVA")
                content["value"] = value
            # Spotify
            elif intent == "SpotifyInfo":
                value = GetJsonData("SPOTIFY")
                content["value"] = value
            # Contact
            elif intent == "Contact":
                value = GetJsonData("CONTACT")
                content["value"] = value
            else:
                value = function_mappings[function_code]()
                # print(value)
                content["value"] = value
    else:
        # For inputs that were not matched...
        content["response"] = "Sorry, I didn't understand that..."
        content["intent"] = "Error"
        content["confidence"] = float(0)
        content["success"] = False
        content["value"] = ""

    return content


# while True:
#     print("How can I help?")
#     query = input("")
#     print(handle_question(query))
