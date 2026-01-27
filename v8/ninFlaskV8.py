from threading import Thread
from flask import Flask, request, render_template
import json
import os
import v8path
from asyncEAGM import EAGM, EAGMError

app = Flask(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "data")
usadata_path = os.path.join(data_dir, "usadata.json")
serverdata_folder_path = os.path.join(data_dir, "serverdata")

BOTTOKEN = v8path.BOTTOKEN
CLIENT_ID = v8path.CLIENT_ID
CLIENT_SECRET = v8path.CLIENT_SECRET
REDIRECT_URI = v8path.REDIRECT_URI

eagm = EAGM(bot_token=BOTTOKEN, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

@app.route("/", methods=["GET"])
async def index():
    # Check if this is an OAuth2 callback
    code = request.args.get("code", "")
    
    if code == "":
        # Show landing page
        return render_template("index.html")
    
    # Handle OAuth2 callback
    try:
        state = request.args.get("state", "").split("=")
        server_id = int(state[0], 16)
        try:
            server_data=json.load(open(os.path.join(serverdata_folder_path, f"{server_id}.json")))
        except:
            return render_template("auth.html", error=True, error_title="エラー", error_message="サーバー情報が見つかりません")

        try:
            get_token = await eagm.get_token(code)
            get_user = await eagm.get_user(get_token.access_token)
        except EAGMError:
            return render_template("auth.html", error=True, error_title="400: 無効なスコープ", error_message="認証に失敗しました"), 400

        addrole = await eagm.add_role(user_id=get_user.user_id, guild_id=server_id, role_id=server_data["role"])
        if addrole!=204:
            return render_template("auth.html", error=True, 
                error_title="ロールの付与に失敗しました",
                error_message="Botがロールを付与できる状態か確認してください。Botのロールが付与したいロールの1つ上に置かれていない場合や、管理権限に2段階認証が必要になっている場合ロールが付与できません！"), 400
        
        try:
            userdata = json.load(open(usadata_path))
        except:
            userdata = {}

        if not get_user.user_id in server_data.keys():
            server_data.update({get_user.user_id:str(len(userdata))})
            json.dump(server_data, open(os.path.join(serverdata_folder_path, f"{server_id}.json"),"w"))

        if not get_token.access_token in userdata.values():
            userdata.update({get_user.user_id:get_token.access_token})
            json.dump(userdata, open(usadata_path,"w"))
        
    except Exception as e:
        return render_template("auth.html", error=True, error_title="エラー", error_message=str(e)), 500

    return render_template("auth.html", success=True, username=get_user.global_name)

@app.route("/setup", methods=["GET"])
def setup():
    return render_template("setup.html")

@app.route("/faq", methods=["GET"])
def faq():
    return render_template("faq.html")

@app.route("/pricing", methods=["GET"])
def pricing():
    return render_template("pricing.html")

def run():
    app.run(debug=False,host="0.0.0.0")

def start():
    Thread(target=run).start()
