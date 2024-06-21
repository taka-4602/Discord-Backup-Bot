import discord
import json
import asyncio
from threading import Thread
import v6path
from EAGM import EAGM

client = discord.Client(intents = discord.Intents.default())
tree = discord.app_commands.CommandTree(client)

usadata_path=v6path.usadata_path
serverdata_folder_path=v6path.serverdata_folder_path
BOTTOKEN=v6path.BOTTOKEN
eagm=EAGM(bot_token=BOTTOKEN)

@client.event
async def on_ready():
    print(f'This is /call! {client.user}')

@tree.command(name="call", description="認証したひと”全員”を追加する")
async def call(interaction: discord.Interaction,データサーバーid:str=None):
    if not interaction.guild:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("管理者しか使えません", ephemeral=True)
        return
    
    alldata = json.load(open(usadata_path))

    if not データサーバーid:
        data_path=open(f"{serverdata_folder_path}{interaction.guild_id}.json")
    elif データサーバーid=="all":
        data_path=open(usadata_path)
    else:
        data_path=open(f"{serverdata_folder_path}{データサーバーid}.json")

    userdata = json.load(data_path)
    a=b=c=d=e=f=0
    for key in list(userdata.keys()):
        addmember=eagm.add_member(access_token=alldata[key],user_id=key,guild_id=str(interaction.guild.id))
        if addmember==201:
            a=a+1
        elif addmember==204:
            b=b+1
        elif addmember==403:
            c=c+1
            del alldata[key]
            del userdata[key]
        elif addmember==429:
            e=e+1
        elif addmember==400:
            f=f+1
        else:
            d=d+1
        
        await asyncio.sleep(1)# <- TooManyRequest対策です！！おこのみの数値または必要ないなら消してください！

    if not データサーバーid:
        json.dump(userdata, open(f"{serverdata_folder_path}{interaction.guild_id}.json","w"))
        json.dump(alldata, open(usadata_path,"w"))
    elif データサーバーid=="all":
        json.dump(userdata, open(usadata_path,"w"))
    else:
        json.dump(userdata, open(f"{serverdata_folder_path}{データサーバーid}.json","w"))
        json.dump(alldata, open(usadata_path,"w"))

    await interaction.channel.send(f"リクエストが終わりました\n{a}人を追加\n{b}人は既に追加されていて\n{c}人の情報が失効済み\n{e}回TooManyRequest\n{f}人はこれ以上サーバーに参加できません\n{d}人は不明なエラーです")

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
    Thread(target=main).start()

def main():
    client.run(BOTTOKEN)
