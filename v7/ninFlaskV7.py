from threading import Thread
from flask import Flask, request
import json
import v7path
from asyncEAGM import EAGM, EAGMError

app = Flask("app")
usadata_path=v7path.usadata_path
serverdata_folder_path=v7path.serverdata_folder_path
BOTTOKEN=v7path.BOTTOKEN

CLIENT_ID = v7path.CLIENT_ID
CLIENT_SECRET = v7path.CLIENT_SECRET
REDIRECT_URI = v7path.REDIRECT_URI

eagm=EAGM(bot_token=BOTTOKEN,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI)

@app.route("/", methods=["GET"])
async def index():
    try:
        code = request.args.get("code", "")
        if code == "":
            return
        state = request.args.get("state", "").split("=")
        server_id = int(state[0],16)
        try:
            server_data=json.load(open(f"{serverdata_folder_path}{server_id}.json"))
        except:
            return

        try:
            await eagm.get_token(code)
            await eagm.get_user(eagm.access_token)
        except EAGMError:
            return "<h1>400: invailed scope</h1>",400
        
        addrole=await eagm.add_role(user_id=eagm.user_id,guild_id=str(server_id),role_id=server_data["role"])
        if addrole!=204:
            return f"<h1>ロールの付与に失敗しました<br>Botがロールを付与できる状態か確認してください<br>Botのロールが付与したいロールの1つ上に置かれていない場合や、管理権限に2段階認証が必要になっている場合ロールが付与できません！</h1>",400

        userdata = json.load(open(usadata_path))

        if not eagm.user_id in server_data.keys():
            server_data.update({eagm.user_id:str(len(userdata))})
            json.dump(server_data, open(f"{serverdata_folder_path}{server_id}.json","w"))     
      
        if not eagm.access_token in userdata.values():
            userdata.update({eagm.user_id:eagm.access_token})
            json.dump(userdata, open(usadata_path,"w"))
        
    except Exception as e:
        return f"<h1>エラー : {e}</h1>",500

    return f"<h1>登録成功！ {eagm.global_name}さんよろしく！</h1>"

def run():
    app.run(debug=False,host="0.0.0.0")

def start():
    Thread(target=run).start()
