import os
import json

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]


def create_credentials():

    creds_json = os.getenv(
        "GMAIL_CREDENTIALS"
    )


    creds_data = json.loads(
        creds_json
    )


    flow = InstalledAppFlow.from_client_config(
        creds_data,
        SCOPES
    )


    creds = flow.run_local_server(
        port=0
    )


    return creds
