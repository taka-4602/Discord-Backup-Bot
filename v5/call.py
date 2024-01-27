import discord
import json
import asyncio
from threading import Thread
import v5path
from EGAM import EGAM

intents = discord.Intents.default()
client = discord.Client(intents = intents)
tree = discord.app_commands.CommandTree(client)

ipath=v5path.ipath
ipath2=v5path.ipath2
BOTTOKEN=v5path.BOTTOKEN
egam=EGAM(bot_token=BOTTOKEN)

@client.event
async def on_ready():
    print(f'This is /call! {client.user}')

@tree.command(name="call", description="認証したひと”全員”を追加する")
async def call(interaction: discord.Interaction,データサーバーid:str=None):
    try:
        if interaction.user.guild_permissions.administrator:
            zenj=open(ipath)
            zendata = json.load(zenj)
            
            if データサーバーid==None:
                useridj=open(f"{ipath2}{interaction.guild_id}.json")
            elif データサーバーid=="all":
                useridj=zenj
            else:
                useridj=open(f"{ipath2}{データサーバーid}.json")
            userid = json.load(useridj)
            a=b=c=d=e=f=0
            for key, value in list(userid.items()):
                addmember=egam.add_member(access_token=zendata[key],user_id=key,guild_id=str(interaction.guild.id))
                if addmember==201:
                    a=a+1
                elif addmember==204:
                    b=b+1
                elif addmember==403:
                    c=c+1
                    del (zendata[f"{key}"])
                    del (userid[f"{key}"])
                elif addmember==429:
                    e=e+1
                elif addmember==400:
                    f=f+1
                else:
                    d=d+1
                
                asyncio.sleep(1)# <- TooManyRequest対策です！！おこのみの数値または必要ないなら消してください！
            if データサーバーid==None:
                json.dump(userid, open(f"{ipath2}{interaction.guild_id}.json","w"))
                json.dump(zendata, open(ipath,"w"))
            elif データサーバーid=="all":
                json.dump(userid, open(ipath,"w"))
            else:
                json.dump(userid, open(f"{ipath2}{データサーバーid}.json","w"))
                json.dump(zendata, open(ipath,"w"))

            await interaction.channel.send(f"リクエストが終わりました\n{a}人を追加\n{b}人は既に追加されていて\n{c}人の情報が失効済み\n{e}回TooManyRequest\n{f}人はこれ以上サーバーに参加できません\n{d}人は不明なエラーです")
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
