import pyrebase

config = {
    "apiKey": "AIzaSyAoU0poXAGUm0QW_9M7_NhxDN2K_e3TeO4",
    "authDomain": "loteria-a4008.firebaseapp.com",
    "databaseURL": "https://loteria-a4008-default-rtdb.firebaseio.com",
    "projectId": "loteria-a4008",
    "storageBucket": "loteria-a4008.appspot.com",
    "messagingSenderId": "305510362883",
    "appId": "1:305510362883:web:14ca1915a9b0f75a794336"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()
auth = firebase.auth()
