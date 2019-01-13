from flask import Flask, session, request, render_template, redirect, url_for, make_response, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import json, os, uuid, redis, hashlib, jwt , datetime, shutil
from datetime import datetime as d8
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode

app = Flask(__name__,static_url_path="/strachob/drive/static")
app.secret_key = b'awi12. as aw23u1[ 82913y'
red = redis.StrictRedis()
oauth = OAuth(app)

with open('./static/config.json') as json_file:
    config_data = json.load(json_file)

auth0 = oauth.register(
    'auth0',
    client_id=config_data['CLIENT_ID'],
    client_secret=config_data['APP_SECRET'],
    api_base_url='https://'+config_data['APP_DOMAIN'],
    access_token_url='https://strachob.eu.auth0.com/oauth/token',
    authorize_url='https://strachob.eu.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)


@app.route('/strachob/drive/')
def index():
    username = username_from_cookies(request.cookies.get('_loginID'))
    if username:
        return redirect(url_for('box'))

    return render_template('index.html')


@app.route('/strachob/drive/off')
def off():
    return render_template('off.html', error="Stick to your own files!")


@app.route('/strachob/drive/no_token')
def no_token():
    return render_template('off.html', error="No token to verify!")


@app.route('/strachob/drive/exp_token')
def exp_token():
    return render_template('off.html', error="Your token has expired!")


@app.route('/strachob/drive/upload_view')
def upload_view():
    username = username_from_cookies(request.cookies.get('_loginID'))
    if username is None:
        return render_template('index.html', error="Login in first!")

    tkn = jwt_token_create_up(username)
    if request.args.get('files') == '1':
        return render_template('upload.html', username=username, tkn=tkn, error="You can only upload 5 files!")
    return render_template('upload.html', username = username, tkn=tkn)

@app.route('/strachob/drive/callback')
def auth_callback():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    
    config_data["JWT_PAYLOAD"] = userinfo
    
    return login_user(userinfo['name'])


@app.route('/strachob/drive/box/')
def box():
    username = username_from_cookies(request.cookies.get('_loginID'))
    if username is None:
        return render_template('index.html', error="Login in first!")

    files_to_show = os.listdir('./files/'+username)

    return render_template('box.html', files=files_to_show, username=username)


@app.route('/strachob/drive/logout', methods=['POST'])
def logout():
    username = username_from_cookies(request.cookies.get('_loginID'))
   
    red.hdel('strachob:drive:sessions', request.cookies.get('_loginID'))
    params = {'returnTo': url_for('index', _external=True), 'client_id': config_data['CLIENT_ID']}
    resp = redirect(auth0.api_base_url + '/logout?' + urlencode(params))
    resp.set_cookie('_loginID', '', expires=0, httponly=True, secure=True)
    return resp


@app.route('/strachob/drive/login', methods=['POST', 'GET'])
def login():
    username = username_from_cookies(request.cookies.get('_loginID'))
    if username:
        return redirect(url_for('box'))

    return auth0.authorize_redirect(redirect_uri='https://127.0.0.1:6887/strachob/drive/callback', audience='https://strachob.eu.auth0.com/userinfo')


@app.route('/strachob/drive/share', methods=['POST'])
def share():
    loggedUser = username_from_cookies(request.cookies.get('_loginID'))
    user = request.form['user']
    if (user != loggedUser):
        return redirect(url_for('off'))

    filename = request.form['file']      
    link = 'https://127.0.0.1:6888/strachob/dl/download?tkn='+jwt_token_create_down(user, filename, True)
    return render_template('box.html', share=filename, username=user, link=link)


@app.route('/strachob/drive/download', methods=['POST'])
def download():
    loggedUser = username_from_cookies(request.cookies.get('_loginID'))
    user = request.form['user']
    if (user != loggedUser):
        return redirect(url_for('off'))
    filename = request.form['file']  
    tkn = jwt_token_create_down(user, filename, False)
    resp  = jsonify()
    resp.status_code= 301
    resp.headers['location'] = 'https://127.0.0.1:6888/strachob/dl/download?tkn='+tkn
    resp.autocorrect_location_header = False
    return resp


def username_from_cookies(cookie):
    user = red.hget('strachob:drive:sessions', cookie)
    
    if user is not None:
        user = user.decode("UTF-8")
        return user

    return None


def login_user(login):
    print(login)
    login_time = datetime.datetime.now()
    login_time = login_time + datetime.timedelta(days=1)
    tkn = str(uuid.uuid4().hex)
    red.hset('strachob:drive:sessions', tkn, login)    
    resp = redirect(url_for('box'))
    resp.set_cookie('_loginID', tkn, expires=login_time, secure=True, httponly=True)
    return resp


def jwt_token_create_down(folder, file_name, long):
    if long:
        tkn = jwt.encode({"usr":folder,"file":file_name }, config_data["DL_JWT_SECRET"], algorithm='HS256')
    else:    
        tkn = jwt.encode({"usr":folder,"file":file_name,"exp": five_min_date() }, config_data["DL_JWT_SECRET"], algorithm='HS256')
    return tkn.decode("UTF-8")


def jwt_token_create_up(folder):
    tkn = jwt.encode({"usr":folder, "exp": five_min_date() }, config_data["DL_JWT_SECRET"], algorithm='HS256')
    return tkn.decode("UTF-8")


def five_min_date():
    login_time = datetime.datetime.now()
    login_time = login_time + datetime.timedelta(minutes=5)
    return login_time

#app.run(port=6887, ssl_context=('cert.pem','key.pem'))
    
