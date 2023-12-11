import discord
import json
import requests
import time
from threading import Thread

intents = discord.Intents.all()
client = discord.Client(intents = intents)
tree = discord.app_commands.CommandTree(client)


ipath="userdata.json のパスをここに"
ipath2="サーバーID.json のフォルダーパスをここに"

BOTTOKEN="Botのトークンをここに

@client.event
async def on_ready():
    print(f'This is /call! {client.user}')

@tree.command(name="call", description="認証したひと”全員”を追加する")
async def call(interaction: discord.Interaction,追加先のサーバーid:str=None,データサーバーid:str=None):
    try:
        if interaction.user.guild_permissions.administrator:
            nj=open("now.json")
            nowj = json.load(nj)
            if nowj["now"] == "1":
                nowj["now"]="0"
                json.dump(nowj, open("now.json","w"))
                nj.close()
                return
            
            nowj["now"]="1"
            json.dump(nowj, open("now.json","w"))
            nj.close()
            await interaction.response.send_message("登録されたユーザーを追加中です...")
            if データサーバーid==None:
                useridj=open(f"{ipath2}{interaction.guild_id}.json")
            else:
                useridj=open(f"{ipath2}{データサーバーid}.json")
            userid = json.load(useridj)
            if 追加先のサーバーid==None:
                guild_id = interaction.guild.id
            else:
                guild_id=追加先のサーバーid
            head = {"Authorization": 'Bot ' + BOTTOKEN, 'Content-Type': 'application/json'}
            a=0
            b=0
            c=0
            d=0
            e=0
            for key, value in list(userid.items()):
                rea=requests.put('https://discord.com/api/guilds/' + f"{guild_id}" + '/members/' + key, headers=head, json={"access_token": value})    
                if rea.status_code==201:
                    a=a+1
                elif rea.status_code==204:
                    b=b+1
                elif rea.status_code==403:
                    c=c+1
                    del (userid[f"{key}"])
                elif rea.status_code==429:
                    e=e+1
                else:
                    d=d+1
                
                #time.sleep()# <- TooManyRequest対策です！！おこのみの数値または必要ないなら消してください！
            if データサーバーid==None:
                json.dump(userid, open(f"{ipath2}{interaction.guild_id}.json","w"))
            else:
                json.dump(userid, open(f"{ipath2}{データサーバーid}.json","w"))
            nj=open("now.json")
            nowj = json.load(nj)
            nowj["now"]="0"
            json.dump(nowj, open("now.json","w"))
            nj.close()
            await interaction.channel.send(f"リクエストが終わりました\n{a}人を追加\n{b}人は既に追加されていて\n{c}人の情報が失効済み\n{e}回TooManyRequest\n{d}人は不明なエラーです")

        else:
            await interaction.response.send_message("管理者しか使えません", ephemeral=True)
            return    
    except:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)


@tree.command(name="button", description="認証ボタンの表示")
async def panel_au(interaction: discord.Interaction,ロール:discord.Role,タイトル:str=None,説明:str=None):
    None
@tree.command(name="check", description="UserIDを使ってTokenを検索する")
async def check(interaction: discord.Interaction,ユーザーid:str):
    None
@tree.command(name="request1", description="UserIDとトークンを使って1人リクエストする")
async def req1(interaction: discord.Interaction,ユーザーid:str):
    None
@tree.command(name="delkey", description="該当ユーザーの情報を削除する")
async def delk(interaction: discord.Interaction,ユーザーid:str):
    None
@tree.command(name="datacheck", description="登録人数の確認")
async def datac(interaction: discord.Interaction):
    None

def callstart():
  c = Thread(target=main)
  c.start()

def main():
    client.run(BOTTOKEN)
