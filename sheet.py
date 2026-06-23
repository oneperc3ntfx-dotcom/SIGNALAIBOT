import requests
import json

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxKL2RLCRPgOE1Y-ZCJ6yrUCZ4Aag4Q94jETKdexOfHJUltIJxtC5Rjq2PE0gqnLPxRXA/exec"


def save_member(data):
    requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(data))


def save_trial(data):
    requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(data))
