import os
from firebaseConf import *
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from datetime import datetime

import jwt
import json



from flask import (
    Flask, 
    render_template,
    redirect, 
    request, 
    url_for,
    g, 
    send_from_directory)

from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,

)
from oauthlib.oauth2 import WebApplicationClient
import requests
import urllib.request
from db import init_db_command
from user import User
import json
import sqlite3
from functools import wraps



GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
certificate_url = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'

google_request = google_requests.Request()

app.config['TEMPLATES_AUTO_RELOAD'] = True
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/static/profileImage.jpg')
def serve_static():
    return send_from_directory(app.static_folder, 'profileImage.jpg')


@app.before_request
def before_request():
    g.user_authenticated = current_user.is_authenticated
    g.profile_pic = get_profile_pic_url(current_user) if current_user.is_authenticated else None
    g.user_ref = auth2.get_user_by_email(current_user.email) if current_user.is_authenticated else None




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
    pass
client = WebApplicationClient(GOOGLE_CLIENT_ID)



@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/', methods=['GET', 'POST'])
def home():
    nombresLoteria=["Euromillones", "Bonoloto", "Primitiva","elGordo"]
    if current_user.is_authenticated:
        profile_pic = current_user.profile_pic        
       
        id_token = current_user.id

        return render_template('home.html', name="logeado" ,profile_pic=profile_pic, resultsEuro=lastResults(), nombresLoterias=nombresLoteria, id=g.user_ref.uid)
    else:
        return render_template('home.html', name='Guest', resultsEuro=lastResults(), nombresLoterias=nombresLoteria)

def lastResults():
    Euromillones=db.child("ultimosresultados/euromillones/resultado").get().val()
    Bonoloto=db.child("ultimosresultados/bonoloto/resultado").get().val()
    Primitiva=db.child("ultimosresultados/primitiva/resultado").get().val()
    ElGordo=db.child("ultimosresultados/elgordo/resultado").get().val()

    return Euromillones, Bonoloto, Primitiva, ElGordo




def get_profile_pic_url(user):
    if user.is_authenticated:
        urllib.request.urlretrieve(user.profile_pic, os.path.join(app.root_path, 'static', 'profileImage.jpg'))

        return user.profile_pic
    else:
        return None
    


def decode_token(token):
    decoded_token = jwt.decode(token, verify=False, algorithms=['RS256'])
    return decoded_token
    

def get_id_token(request):
    id_token_cookie = request.cookies.get("token")
    if id_token_cookie:
        return id_token_cookie
    return None



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
    return render_template('about.html')


@app.route('/add', methods=['GET', 'POST'])
def add():

    if request.method == 'POST':
        print("hola")
        procesar_datos_formulario(request.form)
        return 'Formulario enviado correctamente'

    return render_template('add.html')

def procesar_datos_formulario(datos_formulario):
    # Aquí procesas los datos del formulario
    loteria = datos_formulario['loteria']
    fecha = datos_formulario['fecha']
    apuesta = datos_formulario['apuesta']
    complemento = datos_formulario['complemento']

    fecha2=fecha.replace("-","/")
    fecha_datetime = datetime.strptime(fecha2, "%Y/%m/%d")
    fecha_formateada = fecha_datetime.strftime("%d/%m/%Y")


    #set boleto db
    db.child("users").child(
        g.user_ref.uid).child('boletos').child(fecha+'_'+apuesta+'_'+complemento+'_'+loteria).set(
        {"sorteo": loteria,
        "fecha": fecha_formateada, 
        "numero": apuesta, 
        "extra": complemento,
        "premio": "premio",
        "estado": "pendiente"})

    print(loteria, fecha, apuesta, complemento)
    
@app.route('/marcadores', methods=['GET', 'POST'])
def marcadores():
    if current_user.is_authenticated:

        boletos = db.child("users").child(
        g.user_ref.uid).child('boletos').get().val()
        return render_template('marcadores.html', t=boletos.values())
    else:
            return redirect(url_for('home'))




@app.route('/results', methods=['GET', 'POST'])
def results():
    return render_template('results.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():    
    return render_template('profile.html', profile_pic=g.profile_pic)



if __name__ == '__main__':
    app.run(debug=True)
