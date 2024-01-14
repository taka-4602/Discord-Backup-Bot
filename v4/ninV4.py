import discord
import json
import requests
import time
from ninFlaskV4 import start
from call import callstart
import v4path

intents = discord.Intents.default()
client = discord.Client(intents = intents)
tree = discord.app_commands.CommandTree(client)

ipath=v4path.ipath
ipath2=v4path.ipath2
BOTTOKEN=v4path.BOTTOKEN
authurl=v4path.authurl

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='認証ボタン'))
    print(f'Thankyou for running! {client.user}')
    await tree.sync()

@tree.command(name="button", description="認証ボタンの表示")
async def panel_au(interaction: discord.Interaction,ロール:discord.Role,タイトル:str="こんにちは！",説明:str="リンクボタンから登録して認証完了"):
    try:
        if interaction.user.guild_permissions.administrator:
            embed = discord.Embed(title=タイトル,description=説明,color=discord.Colour.blue())
            button = discord.ui.Button(label="登録リンク", style=discord.ButtonStyle.primary, url=authurl+f"&state={(hex(interaction.guild_id)).upper()[2:]}={(oct(ロール.id)).upper()[2:]}")
            view = discord.ui.View()
            view.add_item(button)
            await interaction.response.send_message("made by ```.taka.``` thankyou for running!!!", ephemeral=True)
            try:
                f=open(f"{ipath2}{interaction.guild.id}.json")
                f2 = json.load(f)
            except:
                f = open(f"{ipath2}{interaction.guild.id}.json","w")
                f.write('{}')
                f.close()
            try:
                await interaction.channel.send(embed = embed, view = view)
            except:
                await interaction.channel.send("メッセージの送信に失敗しました")
                return
        else:
            await interaction.response.send_message("管理者しか使えません", ephemeral=True)
            return    
    except:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)


@tree.command(name="call", description="認証したひと”全員”を追加する")
async def call(interaction: discord.Interaction,データサーバーid:str=None):
    nj=open("now.json")
    now=json.load(nj)
    if now["now"]=="1":
        await interaction.response.send_message(f"現在/call中です", ephemeral=True)


@tree.command(name="check", description="UserIDを使ってTokenを検索する")
async def check(interaction: discord.Interaction,ユーザーid:str):
    try:
        if interaction.user.guild_permissions.administrator:
            useridj=open(ipath)
            userid = json.load(useridj)
            try:
                token=(userid[f"{ユーザーid}"])
                await interaction.response.send_message(f"該当ユーザーのトークンは```{token}```です\nUserID：```{ユーザーid}```", ephemeral=False)

            except:
                await interaction.response.send_message("ユーザー情報が見つかりませんでした", ephemeral=False)

        else:
            await interaction.response.send_message("管理者しか使えません", ephemeral=True)
            return    
    except:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)


@tree.command(name="request1", description="UserIDとトークンを使って1人リクエストする")
async def req1(interaction: discord.Interaction,ユーザーid:str,サーバーid:str=None):
    try:
        if interaction.user.guild_permissions.administrator:
            useridj=open(ipath)
            userid = json.load(useridj)
            try:
                token=(userid[f"{ユーザーid}"])            
                if サーバーid==None:
                    guild_id = interaction.guild.id
                else:
                    guild_id=サーバーid

                head = {"Authorization": 'Bot ' + BOTTOKEN, 'Content-Type': 'application/json'}
                rea=requests.put('https://discord.com/api/guilds/' + f"{guild_id}" + '/members/' + ユーザーid, headers=head, json={"access_token": token})
                print(rea.status_code)
                if rea.status_code==201:
                    await interaction.response.send_message("該当のユーザーを追加しました")   
                elif rea.status_code==204:
                    await interaction.response.send_message("該当のユーザーは既に追加されています")    
                elif rea.status_code==403:
                    await interaction.response.send_message("該当ユーザーの保存情報は失効しています")
                elif rea.status_code==400:
                    await interaction.response.send_message("該当ユーザーはこれ以上サーバーに参加できません")
                elif rea.status_code==429:
                    await interaction.response.send_message("429レートリミットです")

                else:
                    await interaction.response.send_message("該当ユーザーの追加は失敗しました")
            except:
                await interaction.response.send_message("ユーザー情報が見つかりませんでした", ephemeral=False)
        else:
            await interaction.response.send_message("管理者しか使えません", ephemeral=True)
            return    
    except:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)


@tree.command(name="delkey", description="該当ユーザーの情報を削除する")
async def delk(interaction: discord.Interaction,ユーザーid:str):
    try:
        if interaction.user.guild_permissions.administrator:
            useridj=open(ipath)
            userid = json.load(useridj)
            try:
                del (userid[f"{ユーザーid}"])
                json.dump(userid, open(ipath,"w"))
                await interaction.response.send_message(f"該当ユーザーの情報を削除しました\nUserID：```{userid}```", ephemeral=False)

            except:
                await interaction.response.send_message("ユーザー情報が見つかりませんでした", ephemeral=False)
        else:
            await interaction.response.send_message("管理者しか使えません", ephemeral=True)
            return    
    except:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)


@tree.command(name="datacheck", description="登録人数の確認")
async def dck(interaction: discord.Interaction):
    try:
        if interaction.user.guild_permissions.administrator:
            useridj=open(ipath)
            userid = json.load(useridj)
            try:
                i=len(userid)    
                await interaction.response.send_message(f"{i}人のデータが登録されています")
            except:
                await interaction.response.send_message("ファイルが使えなくなっています")
        else:
            await interaction.response.send_message("管理者しか使えません", ephemeral=True)
            return    
    except:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)


start()
time.sleep(1)
callstart()
time.sleep(1)
client.run(BOTTOKEN)
