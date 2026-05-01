from threading import Thread
from flask import Flask, request
import json
import os
import v9path
from asyncEAGM import EAGM, EAGMError

app = Flask("app")

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "data")
usadata_path = os.path.join(data_dir, "usadata.json")
serverdata_folder_path = os.path.join(data_dir, "server_data")

if not os.path.exists(data_dir):
    os.mkdir(data_dir)

if not os.path.exists(serverdata_folder_path):
    os.mkdir(serverdata_folder_path)

BOTTOKEN = v9path.BOTTOKEN
CLIENT_ID = v9path.CLIENT_ID
CLIENT_SECRET = v9path.CLIENT_SECRET
REDIRECT_URI = v9path.REDIRECT_URI

@app.route("/", methods=["GET"])
async def index():
    try:
        code = request.args.get("code", "")
        if code == "":
            return
        
        state = request.args.get("state", "").split("=")
        server_id = int(state[0], 16)
        try:
            with open(os.path.join(serverdata_folder_path, f"{server_id}.json")) as f:
                server_data = json.load(f)
        except:
            return

        eagm = EAGM(BOTTOKEN, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
        try:
            get_token = await eagm.get_token(code)
            get_user = await eagm.get_user(get_token.access_token)
        except EAGMError:
            return "<h1>400: invalid scope</h1>", 400

        add_role = await eagm.add_role(user_id=get_user.user_id, guild_id=server_id, role_id=server_data["role"])
        if add_role != 204:
            return f"<h1>ロールの付与に失敗しました<br>Botがロールを付与できる状態か確認してください<br>Botのロールが付与したいロールの1つ上に置かれていない場合や、管理権限に2段階認証が必要になっている場合ロールが付与できません！</h1>", 400

        try:
            with open(os.path.join(serverdata_folder_path, f"{server_id}.json")) as f:
                userdata = json.load(f)
        except:
            userdata = {}

        if not get_user.user_id in server_data.keys():
            server_data.update({get_user.user_id:str(len(userdata))})
            with open(os.path.join(serverdata_folder_path, f"{server_id}.json"),"w") as f:
                json.dump(server_data, f)

        if not get_token.access_token in userdata.values():
            userdata.update({get_user.user_id:get_token.access_token})
            with open(usadata_path,"w") as f:
                json.dump(userdata, f)
        
    except Exception as e:
        return f"<h1>エラー : {e}</h1>", 500

    return f"<h1>登録成功！ {get_user.global_name}さんよろしく！</h1>"

def run():
    app.run(debug=False,host="0.0.0.0")

def start():
    Thread(target=run).start()