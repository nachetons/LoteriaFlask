import pyrebase
from firebase_admin import credentials,initialize_app
from firebase_admin import auth as auth2
import os

API_KEY = os.environ.get('API_KEY', None)
AUTH_DOMAIN = os.environ.get('AUTH_DOMAIN', None)
DATABASE_URL = os.environ.get('DATABASE_URL', None)
PROJECT_ID = os.environ.get('PROJECT_ID', None)
STORAGE_BUCKET = os.environ.get('STORAGE_BUCKET', None)
MESSAGING_SENDER_ID = os.environ.get('MESSAGING_SENDER_ID', None)
APP_ID = os.environ.get('APP_ID', None)

config = {
    "apiKey": API_KEY,
    "authDomain": AUTH_DOMAIN,
    "databaseURL": DATABASE_URL,
    "projectId": PROJECT_ID,
    "storageBucket": STORAGE_BUCKET,
    "messagingSenderId": MESSAGING_SENDER_ID,
    "appId": APP_ID
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


cred = credentials.Certificate("admin.json")
default_app = initialize_app(cred, {'databaseURL': DATABASE_URL})







