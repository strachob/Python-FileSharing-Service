from flask import Flask, session, request, render_template, redirect, url_for, make_response, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import json, os, uuid, redis, hashlib, jwt , datetime, shutil
from datetime import datetime as d8

red = redis.StrictRedis()
app = Flask(__name__,static_url_path="/strachob/drive/static")
app.secret_key = b'awi12. as aw23u1[ 82913y'



@app.route('/strachob/drive/')
def index():
    username = username_from_cookies(request.cookies.get('_loginID'))
    if username:
        return redirect(url_for('box'))

    return render_template('index.html')


@app.route('/strachob/drive/box/')
def box():
    if request.args.get('f') == '2':
        return render_template('off.html', error="Your token has expired!")
    elif request.args.get('f') == '3':
        return render_template('off.html', error="No token to verify!")

    username = username_from_cookies(request.cookies.get('_loginID'))
    if username is None:
        return render_template('index.html', error="Login in first!")

    tkn = jwt_token_create_up(username)
    files_to_show = os.listdir('./files/'+username)
    if request.args.get('f') == '1':
        return render_template('box.html', files=files_to_show, username=username, tkn=tkn, error="You can only upload 5 files!")
    return render_template('box.html', files=files_to_show, username=username, tkn=tkn )


@app.route('/strachob/drive/regiform/')
def regiform():
    return render_template('register.html')


@app.route('/strachob/drive/logout', methods=['POST'])
def logout():
    username = username_from_cookies(request.cookies.get('_loginID'))
    resp = make_response(render_template('index.html', error="Logout successful!"))
    resp.set_cookie('_loginID', '', expires=0)
   
    red.hdel('strachob:drive:sessions', request.cookies.get('_loginID'))

    return resp


@app.route('/strachob/drive/register', methods=['POST'])
def register():
    username = search_for_user(request.form['login'])

    if username:
        return render_template('register.html', error='Email already taken!')

    if("../" in request.form['login']):
        return render_template('register.html', error='Email contains forbiden sequence of characters')
    register_new_user(request.form['name'], request.form['login'], request.form['password'])
    
    return render_template('index.html', error="Register successful!")


@app.route('/strachob/drive/login', methods=['POST', 'GET'])
def login():
    username = username_from_cookies(request.cookies.get('_loginID'))
    if username:
        return redirect(url_for('box'))

    if request.method == "GET":
        return redirect(url_for('index'))

    error = None
    if request.method == 'POST':
        if validate_login(request.form['login'], request.form['pass']):
            return login_user(request.form['login'])
        else:
            error = 'Invalid email/password'

    return render_template('index.html', error=error)


@app.route('/strachob/drive/download/<user>/<filename>', methods=['GET'])
def download(user, filename):
    loggedUser = username_from_cookies(request.cookies.get('_loginID'))
    if (user != loggedUser):
        return redirect(url_for('off'))
    tkn = jwt_token_create_down(user, filename)
    resp  = jsonify()
    resp.status_code= 301
    resp.headers['location'] = 'https://pi.iem.pw.edu.pl/strachob/dl/download?tkn='+tkn
    resp.autocorrect_location_header = False
    return resp


@app.route('/strachob/drive/off')
def off():
    return render_template('off.html', error="Stick to your own files!")


def search_for_user(email):
    db_user = red.hget('strachob:drive:'+email, 'login')
    if db_user is not None:
        if db_user.decode("UTF-8") == email:
            return True
    
    return False
    

def validate_login(username, password):
    db_user = red.hget('strachob:drive:'+username, 'login')
    if db_user is None:
        return False
    db_user = db_user.decode("UTF-8")
    db_pass = red.hget('strachob:drive:'+username, 'passwd')
    db_pass = db_pass.decode("UTF-8")
    db_salt = red.hget('strachob:drive:'+username, 'salt')
    db_salt = db_salt.decode("UTF-8")

    hash_passwd = hashlib.sha1()
    hash_passwd.update(('%s%s' % (db_salt, password)).encode('utf-8'))
    try_pass = hash_passwd.hexdigest()
    if db_user == username:
        if try_pass == db_pass:
            return True

    return False


def username_from_cookies(cookie):
    user = red.hget('strachob:drive:sessions', cookie)
    
    if user is not None:
        user = user.decode("UTF-8")
        return user

    return None


def login_user(login):
    login_time = datetime.datetime.now()
    login_time = login_time + datetime.timedelta(days=1)
    resp = redirect(url_for('box'))
    resp.set_cookie('_loginID', new_cookie(login), expires=login_time, secure=True, httponly=True)
    return resp
   

def register_new_user(name, login, password):
    salt = os.urandom(4).hex()
    hash_passwd = hashlib.sha1()
    hash_passwd.update(('%s%s' % (salt, password)).encode('utf-8'))

    red.hset('strachob:drive:' + login,'login', login)
    red.hset('strachob:drive:' + login,'passwd', hash_passwd.hexdigest())
    red.hset('strachob:drive:' + login,'salt' ,salt)
    red.hset('strachob:drive:' + login,'name' ,name)

    os.makedirs('./files/'+ login)


def new_cookie(login):
    tkn = str(uuid.uuid4().hex)
    red.hset('strachob:drive:sessions', tkn, login)    
    return tkn   


def jwt_token_create_down(folder, file_name):
    tkn = jwt.encode({"usr":folder,"file":file_name,"exp": five_min_date() }, 'S3crt', algorithm='HS256')
    return tkn.decode("UTF-8")


def jwt_token_create_up(folder):
    tkn = jwt.encode({"usr":folder, "exp": five_min_date() }, 'S3crt', algorithm='HS256')
    return tkn.decode("UTF-8")


def five_min_date():
    login_time = datetime.datetime.now()
    login_time = login_time + datetime.timedelta(minutes=5)
    return login_time



def check_files_folder():
    for user in os.listdir('./files'):
        if red.hget('strachob:drive:'+user, 'login') is None:
            shutil.rmtree('./files/' + user)


check_files_folder()
    
