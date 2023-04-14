import os
from firebaseConf import *

from flask import Flask, render_template, session, abort, redirect, request, url_for, send_file

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,

)
from oauthlib.oauth2 import WebApplicationClient
import requests
from db import init_db_command
from user import User
import json
import sqlite3


GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


app.config['TEMPLATES_AUTO_RELOAD'] = True
# to allow Http traffic for local dev
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return user_id


@login_manager.unauthorized_handler
def unauthorized():
    init_db_command()

    return "You must be logged in to access this content.", 403



try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass
client = WebApplicationClient(GOOGLE_CLIENT_ID)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/', methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        filename = 'static/FotoCarnet.jpg'
        send_file(filename, mimetype='image/jpg')
        return render_template('home.html', name="logeado", img=filename)
    else:
        filename = 'static/Google_icon.png'
        send_file(filename, mimetype='image/png')
        return render_template('home.html', name='Guest', img=filename)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login/callback")
def callback():
    code = request.args.get('code')
    google_provider_cfg = get_google_provider_cfg()

    token_endpoint = google_provider_cfg['token_endpoint']

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    user_info = userinfo_response.json()

    print(user_info)

    if user_info.get("email_verified"):
        unique_id = user_info['sub']
        users_email = user_info['email']
        picture = user_info['picture']
        users_name = user_info['given_name']

    else:
        return "User email not available or not verified by Google.", 400

    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )


    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    login_user(user)


    return redirect(url_for('home'))


@app.route('/about', methods=['GET', 'POST'])
def about():
    data = []
    # ref = db.reference('users').child('jaZWAoZQn6yKbOERUtL2')
    return render_template('about.html')


@app.route('/marcadores', methods=['GET', 'POST'])
def marcadores():
    boletos = db.child("users").child(
        'aqgquryQOHhk20mbcy1GKDsD7932').child('boletos').get().val()
    return render_template('hello.html', t=boletos.values())


@app.route('/results', methods=['GET', 'POST'])
def results():
    return render_template('results.html')


if __name__ == '__main__':
    app.run(debug=True)
