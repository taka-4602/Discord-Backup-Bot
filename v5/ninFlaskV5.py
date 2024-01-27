from threading import Thread
from flask import Flask, request
import json
import v5path
from EGAM import EGAM

app = Flask("app")
ipath=v5path.ipath
ipath2=v5path.ipath2
BOTTOKEN=v5path.BOTTOKEN

CLIENT_ID = v5path.CLIENT_ID
CLIENT_SECRET = v5path.CLIENT_SECRET
REDIRECT_URI = v5path.REDIRECT_URI

egam=EGAM(bot_token=BOTTOKEN,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI)

@app.route('/', methods=["GET"])
def index():
    try:
        code = request.args.get('code', '')
        if code == "":
          return
        state = request.args.get('state', '').split("=")
        serverstate=int(state[0],16)
        rolestate=int(state[1],8)
        try:
          serveridj = open(f"{ipath2}{serverstate}.json")
        except:
          return
        
        gettoken= egam.get_token(code)
        token = gettoken['access_token']
        getuser = egam.get_user(token)
        user = getuser["id"]
        name = getuser["username"]
        addrole=egam.add_role(user_id=user,guild_id=str(serverstate),role_id=str(rolestate))
        if not addrole==204:
          return f"<h1>ロールの付与に失敗しました<br>Botがロールを付与できる状態か確認してください<br>Botのロールが付与したいロールの1つ上に置かれていない場合や、管理権限に2段階認証が必要になっている場合ロールが付与できません！</h1>"

        serverid=json.load(serveridj)   
        useridj=open(ipath)
        userid = json.load(useridj)

        if not user in serverid.keys():
          serverid.update({user:f"{len(userid)}"})
          json.dump(serverid, open(f"{ipath2}{serverstate}.json","w"))     
      
        if not token in userid.values():
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
