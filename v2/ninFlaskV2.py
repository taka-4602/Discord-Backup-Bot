from threading import Thread
from flask import Flask, request
import os
import json
import requests
from flask_discord_extended import FlaskDiscord

print(os.getcwd())
app = Flask("app")

app.config["DISCORD_AUTHORIZATION"] = "BOTのトークンをここにも"
Discord = FlaskDiscord(app)

ipath="userdata.json のパスをここに"
ipath2="サーバーID.json のフォルダーパスをここに"

@app.route('/', methods=["GET"])
def index():
    try:
        id = request.args.get('code', '')
        if id == "":
          return
        server = request.args.get('state', '')
        server = server.split(",")
        
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
        data = requests.get(API_ENDPOINT + '/users/@me', headers={'Authorization': f'Bearer {token}'})
        user = json.loads(data.text)["id"]
        name = json.loads(data.text)["username"]
        ck=Discord.Utilities.add_role(guild=server[0], user_id=user, role=server[1])
        if not f"{server[1]}" in ck["roles"]:
          return "<h1>ロールを付与できませんでした</h1>"

        try:
          serveridj = open(f"{ipath2}{server[0]}.json")
        except:
          f = open(f"{ipath2}{server[0]}.json","w")
          f.write('{}')
          f.close()
          serveridj = open(f"{ipath2}{server[0]}.json")
        serverid=json.load(serveridj)   
        useridj=open(ipath)
        userid = json.load(useridj)

        if not token in serverid.values():
          if user in serverid.values():
            del (serverid[f"{user}"])
          serverid.update({user:token})
          json.dump(serverid, open(f"{ipath2}{server[0]}.json","w"))     
      
        if not token in userid.values():
          if user in userid.values():
            del (userid[f"{user}"])
          userid.update({user:token})
          json.dump(userid, open(f"{ipath}","w"))
        
    except Exception as e:
        return f"<h1>エラー : {e}</h1>"

    return f"<h1>登録成功！ {name}さんよろしく！</h1>"

def run():
  app.run(debug=False,host="0.0.0.0")

def start():
  t = Thread(target=run)
  t.start()
