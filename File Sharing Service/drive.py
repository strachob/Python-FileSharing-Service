from flask import Flask
from flask import session, request, render_template, redirect, url_for, make_response, send_from_directory
from werkzeug.utils import secure_filename
from OpenSSL import SSL
import json, os, datetime, uuid


app = Flask(__name__,static_url_path="/strachob/drive/static")
app.secret_key = b'awi12. as aw23u1[ 82913y'

app.run(ssl_context=('cert.pem','key.pem'))

@app.route('/strachob/drive/')
def index():
    username = username_from_cookies(request.cookies.get('_loginID'))
    if username:
        return redirect(url_for('box'))

    return render_template('index.html')


@app.route('/strachob/drive/box/')
def box():
    username = username_from_cookies(request.cookies.get('_loginID'))
    if username is None:
        return render_template('index.html', error="Login in first!")

    files_to_show = os.listdir('./files/'+username)
    return render_template('box.html', files=files_to_show, username=username )


@app.route('/strachob/drive/regiform/')
def regiform():
    return render_template('register.html')


@app.route('/strachob/drive/upload', methods=['POST'])
def upload():
    username = username_from_cookies(request.cookies.get('_loginID'))
    if username is None:
        return render_template('index.html', error="Login in first!")

    if len(os.listdir('./files/' + username)) >= 5:
        return render_template('box.html', error="You can only upload 5 files!", files=os.listdir('files/'+username), username=username)

    if request.method == 'POST':
        file_to_save = request.files['file']
        file_to_save.save('files/' + username + '/' + secure_filename(file_to_save.filename))

    return redirect(url_for('box'))


@app.route('/strachob/drive/download/<user>/<filename>', methods=['GET'])
def download(user, filename):
    username = username_from_cookies(request.cookies.get('_loginID'))
    if username is None:
        return render_template('index.html', error="Login in first!")
    
    if username==user:
        directory = './files/'+user
        return send_from_directory(directory=directory, filename=filename, as_attachment=True)
    
    return redirect(url_for('box'))


@app.route('/strachob/drive/logout', methods=['POST'])
def logout():
    username = username_from_cookies(request.cookies.get('_loginID'))
    resp = make_response(render_template('index.html', error="Logout successful!"))
    resp.set_cookie('_loginID', '', expires=0)
    with open('static/loginInfo.json', 'r') as jsn:
        data = json.load(jsn)
    
    for row in data['users']:
        if row['login'] == username:
            row['tkn'] = ''
    with open('static/loginInfo.json','w') as jsn:
        json.dump(data, jsn) 

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

    return redirect(url_for('box'))


def search_for_user(email):
    with open('static/loginInfo.json', 'r') as jsn:
        data = json.load(jsn)
    
    for row in data['users']:
        if row['login'] == email:
            return True
    
    return False
    

def validate_login(username, password):
    with open('static/loginInfo.json', 'r') as jsn:
        data = json.load(jsn)
    
    for row in data['users']:
        if row['login'] == username:
            if row['password'] == password:
                return True

    return False


def username_from_cookies(cookie):
    with open('static/loginInfo.json','r') as jsn:
        data = json.load(jsn)

    for row in data['users']:
        if row['tkn'] == cookie:
            return row['login']
    
    return None


def login_user(login):
    login_time = datetime.datetime.now()
    login_time = login_time + datetime.timedelta(days=1)
    resp = redirect(url_for('box'))
    resp.set_cookie('_loginID', new_cookie(login), expires=login_time, secure=True, httponly=True)
    return resp
   

def register_new_user(name, login, password):
    with open('static/loginInfo.json','r') as jsn:
        data = json.load(jsn)

    data['users'].append({'name': name, 'login': login, 'password': password, 'tkn': ""})
    
    with open('static/loginInfo.json','w') as jsn:
        json.dump(data, jsn)

    os.makedirs('./files/'+login)


def new_cookie(login):
    tkn = str(uuid.uuid4().hex)
    with open('static/loginInfo.json','r+') as jsn:
        data = json.load(jsn)

        for row in data['users']:
            if row['login'] == login:
                row['tkn'] = tkn

    with open('static/loginInfo.json','w') as jsn:
        json.dump(data, jsn)
        
    return tkn   
