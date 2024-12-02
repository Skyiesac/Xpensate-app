from google.oauth2 import service_account
import google.auth.transport.requests
import requests
from decouple import config
import logging

SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

def get_firebase_access_token():
    credentials = service_account.Credentials.from_service_account_file(
    config('FIREBASE_SERVICE_ACCOUNT_PATH'),
    scopes=SCOPES
)
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

def send_firebase_notification(fcm_token, title, body):
    """
    Sends a notification via Firebase Cloud Messaging API.
    """
    url = "https://fcm.googleapis.com/v1/projects/xpensate-c82e9/messages:send"  
    payload = {
        "message": {
            "token": fcm_token,
            "notification": {
                "title": title,
                "body": body
            }
        }
    }
    
    access_token = get_firebase_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status() 