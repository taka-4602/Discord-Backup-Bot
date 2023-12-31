from threading import Thread
from flask import Flask, request
import os
import json
import requests

print(os.getcwd())
app = Flask("app")

ipath="userdata.json のパスをここに"

@app.route('/', methods=["GET"])
def index():
    try:
        id = request.args.get('code', '')
        print(id)
        if id == "":
          return
        API_ENDPOINT = 'https://discord.com/api/v10'
        CLIENT_ID = ['OAuth2のClientIDをここに']
        my_secret = ['OAuth2のClientSecretをここに']
        CLIENT_SECRET = my_secret
        REDIRECT_URI = 'Flaskサーバーが建てられている場所(IPアドレスやドメイン)をここに'
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': id,
            'redirect_uri': REDIRECT_URI
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
        r.raise_for_status()
        token = json.loads(r.text)['access_token']
        print(token)
        data = requests.get(API_ENDPOINT + '/users/@me', headers={'Authorization': f'Bearer {token}'})
        user = json.loads(data.text)["id"]
        print(user)
        name = json.loads(data.text)["username"]
        print(name)     

        useridj=open(ipath)
        userid = json.load(useridj)

        if token in userid.values():
               return f"<h1>{name}さん、あなたはすでに登録されています！</h1>" 
        if user in userid.values():
            del (userid[f"{user}"])
        try:                  
            userid.update({user:token})
            json.dump(userid, open(ipath,"w"))

        except Exception as e:
            return f"<h1>エラー : {e}</h1>"        
        
    except Exception as e:
        return f"<h1>エラー : {e}</h1>"
    
    return f"<h1>登録成功！ {name}さんよろしく！</h1>"

def run():
  app.run(debug=False,host="0.0.0.0")

def start():
  t = Thread(target=run)
  t.start()
