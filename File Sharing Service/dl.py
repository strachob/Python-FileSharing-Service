from flask import Flask, session, request, render_template, redirect, url_for, make_response, send_from_directory
from werkzeug.utils import secure_filename
import json, os, datetime, uuid, jwt, requests, pika
from datetime import datetime as d8
from shutil import copyfile

app = Flask(__name__,static_url_path="/strachob/drive/static")

with open('./static/config.json') as json_file:
    config_data = json.load(json_file)

@app.route('/strachob/dl/upload', methods=['POST'])
def upload():
    if request.form['tkn'] is None:
        return redirect('https://127.0.0.1:6887/strachob/drive/no_token')
    
    
    if(request.files['file'] is None):
        print("ok")
    verifiedData = verifyUser(str(request.form['tkn']))
    if verifiedData is not None:
        if verifiedData == "Your token has expired":
            return redirect('https://127.0.0.1:6887/strachob/drive/exp_token')

        if len(os.listdir('./files/' + verifiedData['usr'])) >= 5:
            return redirect('https://127.0.0.1:6887/strachob/drive/upload_view?files=1')


        file_to_save = request.files['file']
        path_to_save = 'files/' + verifiedData['usr'] + '/' + secure_filename(file_to_save.filename)
        file_to_save.save(path_to_save)
        
        if file_to_save.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            copyfile('./static/icons/def-icon.png','./static/icons/'+ verifiedData['usr'] + '/' + secure_filename(file_to_save.filename)+'.icon.png')
            push_to_queue(path_to_save)

        try:
            requests.post('https://127.0.0.1:6889/strachob/events/notify/'+verifiedData['usr'], data={'file':file_to_save.filename}, verify=False)
        except requests.exceptions.RequestException as e:
            print('Server Node is not working at the time')

    return redirect('https://127.0.0.1:6887/strachob/drive/box')
    

@app.route('/strachob/dl/download', methods=['GET', 'POST'])
def download():
    if request.args.get('tkn') is None:
        return redirect('https://127.0.0.1:6887/strachob/drive/no_token')
    verifiedData = verifyUser(request.args.get('tkn'))
    if verifiedData is not None:
        if verifiedData == "Your token has expired":
            return redirect('https://127.0.0.1:6887/strachob/drive/exp_token')
        directory = './files/'+ verifiedData['usr']
        return send_from_directory(directory=directory, filename=secure_filename(verifiedData['file']), as_attachment=True)
    
    return redirect('https://127.0.0.1:6887/strachob/drive/exp_token')
   

def verifyUser(tkn):
    try:
        data_decoded = jwt.decode(tkn, config_data["DL_JWT_SECRET"], algorithms=['HS256'])
        return data_decoded
    except:
        return "Your token has expired"

def push_to_queue(path_to_file):
    exchange = 'strachob_pictures'
    exchange_type = 'direct'
    routing_key = 'miniturize'

    print("==> %s ==> %s (%s)" % (routing_key, exchange, exchange_type))
    body = path_to_file

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange,
                         exchange_type=exchange_type)
    channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=body)
    print(" [x] Sent '{}'".format(body))
    connection.close()

#app.run(port=6888, ssl_context=('cert.pem','key.pem'))

