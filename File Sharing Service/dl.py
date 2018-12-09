from flask import Flask, session, request, render_template, redirect, url_for, make_response, send_from_directory
from werkzeug.utils import secure_filename
import json, os, datetime, uuid, jwt, requests
from datetime import datetime as d8

app = Flask(__name__,static_url_path="/strachob/drive/static")


@app.route('/strachob/dl/upload', methods=['POST'])
def upload():
    if request.form['tkn'] is None:
        return redirect('https://pi.iem.pw.edu.pl/strachob/drive/no_token')
    verifiedData = verifyUser(str(request.form['tkn']))
    if verifiedData is not None:
        if verifiedData == "Your token has expired":
            return redirect('https://pi.iem.pw.edu.pl/strachob/drive/exp_token')

        if len(os.listdir('./files/' + verifiedData['usr'])) >= 5:
            return redirect('https://pi.iem.pw.edu.pl/strachob/drive/box?files=1')

        file_to_save = request.files['file']
        file_to_save.save('files/' + verifiedData['usr'] + '/' + secure_filename(file_to_save.filename))
        requests.post('https://pi.iem.pw.edu.pl:6889/strachob/events/notify/'+verifiedData['usr'], data={'file':file_to_save.filename}, verify=False)

    return redirect('https://pi.iem.pw.edu.pl/strachob/drive/box')
    

@app.route('/strachob/dl/download', methods=['GET', 'POST'])
def download():
    if request.args.get('tkn') is None:
        return redirect('https://pi.iem.pw.edu.pl/strachob/drive/no_token')
    verifiedData = verifyUser(request.args.get('tkn'))
    if verifiedData is not None:
        if verifiedData == "Your token has expired":
            return redirect('https://pi.iem.pw.edu.pl/strachob/drive/exp_token')
        directory = './files/'+ verifiedData['usr']
        return send_from_directory(directory=directory, filename=secure_filename(verifiedData['file']), as_attachment=True)
    
    return redirect('https://pi.iem.pw.edu.pl/strachob/drive/exp_token')
   

def verifyUser(tkn):
    try:
        data = jwt.decode(tkn, 'S3crt', algorithms=['HS256'])
        return data
    except:
        return "Your token has expired"

#app.run(port=6888, ssl_context=('cert.pem','key.pem'))
