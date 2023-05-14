from scripts.dependencies import *

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/about', methods=['GET', 'POST'])
def about():
    data = []
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
            flash("Boleto eliminado correctamente", "success")
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

        dias = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
        años = ['2016', '2017', '2018', '2019', '2020', '2021','2022', '2023'];

        duracion=[]
        balance=[]
        fechas=[]

        duracion.clear
        balance.clear
        fechas.clear

        if request.method == 'POST':
            seleccion = request.json['seleccion']
            if seleccion == 'Semana':
                print("semana")
                resultados = getAllBalance(g.user_ref.uid, seleccion)
                balance.append(resultados.values())
                fechas.append(resultados.keys())
                for i in range(7):
                    duracion.append(dias[i])
            elif seleccion == 'Mes':
                print("mes")
                resultados = getAllBalance(g.user_ref.uid, seleccion)
                balance.append(resultados.values())
                fechas.append(resultados.keys())
                for i in range(12):
                    duracion.append(meses[i])
            elif seleccion == 'Año':
                resultados = getAllBalance(g.user_ref.uid, seleccion)
                balance.append(resultados.values())
                fechas.append(resultados.keys())
                print("año")
                for i in range(8):
                    duracion.append(años[i])
            graph_data = graph(duracion, balance, fechas)
            return jsonify(graph_data)
        else:
            return render_template('results.html')
        
    else:
        return redirect(url_for('home'))

def graph(duration, balance, fechas):
#    y = [50, 200, 100, 230, 900, 0, 500,900, 200, 500, 0, 900, 0, 500]
    fechas = list(fechas[0])
    balance = list(balance[0])
   
    
    
    print(balance)
    print(fechas)
   
    x = duration
    y = balance
    trace = {
        'x': x,
        'y': y,
        'mode': 'lines+markers',
        'line': {
            'color': 'rgb(0, 123, 255)',
            'width': 4,
            'shape': 'spline'
        }
    }
    data = [trace]
    layout = {
        'xaxis': {
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 1,
            'tickvals': list(range(len(x))), # Ajusta el número de ticks en el eje x
            'ticktext': x
        },
        'yaxis': {
            'range': [0, 1000],
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 200
        }
    }
    return {'data': data, 'layout': layout}



    



@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():    
    return render_template('profile.html', profile_pic=g.profile_pic)



if __name__ == '__main__':
    app.run(debug=True)


