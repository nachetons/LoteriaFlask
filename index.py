from flask import session
from scripts.dependencies import *

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
SERVER = os.environ.get('SERVER', None)
PORT = os.environ.get('PORT', None)
EMAIL = os.environ.get('EMAIL', None)
PASSWORD = os.environ.get('PASSWORD', None)
TLS = os.environ.get('TLS', None)
SSL = os.environ.get('SSL', None)



app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config['MAIL_SERVER']= SERVER
app.config['MAIL_PORT'] = PORT
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = PASSWORD
app.config['MAIL_USE_SSL'] = SSL
mail = Mail(app)

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
        

        return render_template('home.html', name="logeado" ,profile_pic=profile_pic, resultsEuro=lastResults(), nombresLoterias=nombresLoteria, id=g.user_ref.uid)
    else:
        return render_template('home.html', name='Guest', resultsEuro=lastResults(), nombresLoterias=nombresLoteria)



def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


def get_profile_pic_url(user):
    if user.is_authenticated:
        urllib.request.urlretrieve(user.profile_pic, os.path.join(app.root_path, 'static', 'profileImage.jpg'))

        return user.profile_pic
    else:
        return None
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
    try:
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        token_response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        return f"HTTP error occurred: {err}", 500
    except requests.exceptions.RequestException as err:
        return f"An error occurred: {err}", 500

    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    try:
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo_response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        return f"HTTP error occurred: {err}", 500
    except requests.exceptions.RequestException as err:
        return f"An error occurred: {err}", 500

    user_info = userinfo_response.json()

    if "email_verified" in user_info and user_info["email_verified"]:
        unique_id = user_info['sub']
        users_email = user_info['email']
        picture = user_info['picture']
        users_name = user_info['given_name']
    else:
        return "User email not available or not verified by Google.", 400

    def create_or_get_user(unique_id, users_name, users_email, picture):
        if not User.get(unique_id):
            User.create(unique_id, users_name, users_email, picture)
        return User(id_=unique_id, name=users_name, email=users_email, profile_pic=picture)

    user = create_or_get_user(unique_id, users_name, users_email, picture)

    session['user_id'] = unique_id
    session['user_name'] = users_name
    session['user_email'] = users_email
    session['user_picture'] = picture
    login_user(user)

    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'POST':

        procesar_datos_email(request.form, EMAIL, mail)

    return render_template('about.html')


@app.route('/add', methods=['GET', 'POST'])
def add():
    if current_user.is_authenticated:
        if request.method == 'POST':
            if 'image' in request.files:
                archivo = request.files['image']
                sendImage(archivo)
                return render_template('add.html')

            else:
                procesar_datos_formulario(request.form, g.user_ref.uid)
                return render_template('add.html')

    else:
        return redirect(url_for('home'))
    
    return render_template('add.html')


def sendImage(image):
    template = cv2.imread('static/templates/euromillonesTemplate.png')
    image.save(os.path.join(app.root_path, 'temp', 'image.jpg'))
    
    image2 = cv2.imread(os.path.join(app.root_path, 'temp', 'image.jpg'))
    align_images(image2,template,g.user_ref.uid)
  

@app.route('/marcadores', methods=['GET', 'POST'])
def marcadores():
    if current_user.is_authenticated:
        boletos = database.getBoletos(g.user_ref.uid)
        if request.method == 'POST':
            return delete(request.form)
        
        return render_template('marcadores.html', t=boletos)
    else:
        return redirect(url_for('home'))
    
def delete(info):
    if request.method == 'POST':
        procesar_datos_formulario2(info['data'], g.user_ref.uid)
        return redirect(url_for('marcadores'))
    else:
        return redirect(url_for('marcadores'))
    


@app.route('/results', methods=['GET', 'POST'])
def results():
    if current_user.is_authenticated:
        if request.method == 'POST':
            seleccion = request.json['seleccion']
            duracion, balance, fechas, date = procesar_datos_grafico(seleccion, g.user_ref.uid)

            graph_data = graph(duracion, balance, fechas, date)
            return jsonify(graph_data)
        else:
            return render_template('results.html')
        
    else:
        return redirect(url_for('home'))



@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():    
    return render_template('profile.html', profile_pic=g.profile_pic)



if __name__ == '__main__':
    app.run(debug=True)

