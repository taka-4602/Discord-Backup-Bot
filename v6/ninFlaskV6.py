from threading import Thread
from flask import Flask, request
import json
import v6path
from EAGM import EAGM

app = Flask("app")
usadata_path=v6path.usadata_path
serverdata_folder_path=v6path.serverdata_folder_path
BOTTOKEN=v6path.BOTTOKEN

CLIENT_ID = v6path.CLIENT_ID
CLIENT_SECRET = v6path.CLIENT_SECRET
REDIRECT_URI = v6path.REDIRECT_URI

eagm=EAGM(bot_token=BOTTOKEN,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI)

@app.route("/", methods=["GET"])
def index():
    try:
        code = request.args.get("code", "")
        if code == "":
            return
        state = request.args.get("state", "").split("=")
        serverstate = int(state[0],16)
        rolestate = int(state[1],8)
        try:
            open(f"{serverdata_folder_path}{serverstate}.json")
        except:
            return

        eagm.get_token(code)
        eagm.get_user(eagm.access_token)
        addrole=eagm.add_role(user_id=eagm.user_id,guild_id=str(serverstate),role_id=str(rolestate))
        if addrole!=204:
            return f"<h1>ロールの付与に失敗しました<br>Botがロールを付与できる状態か確認してください<br>Botのロールが付与したいロールの1つ上に置かれていない場合や、管理権限に2段階認証が必要になっている場合ロールが付与できません！</h1>"

        serverid = json.load(open(f"{serverdata_folder_path}{serverstate}.json"))
        userdata = json.load(open(usadata_path))

        if not eagm.user_id in serverid.keys():
            serverid.update({eagm.user_id:str(len(userdata))})
            json.dump(serverid, open(f"{serverdata_folder_path}{serverstate}.json","w"))     
      
        if not eagm.access_token in userdata.values():
            userdata.update({eagm.user_id:eagm.access_token})
            json.dump(userdata, open(usadata_path,"w"))
        
    except Exception as e:
        return f"<h1>エラー : {e}</h1>"

    return f"<h1>登録成功！ {eagm.global_name}さんよろしく！</h1>"

def run():
    app.run(debug=False,host="0.0.0.0")

def start():
    Thread(target=run).start()
