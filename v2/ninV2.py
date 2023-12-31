import discord
import json
import requests
from ninFlaskV2 import start


intents = discord.Intents.all()
client = discord.Client(intents = intents)
tree = discord.app_commands.CommandTree(client)


ipath="userdata.json のパスをここに"
ipath2="サーバーID.json のフォルダーパスをここに"

BOTTOKEN="Botのトークンをここに"
authurl="作ったURLをここに"

@client.event
async def on_ready():
    await client.change_presence(activity=discord. Activity(type=discord.ActivityType.watching, name='認証ボタン'))
    print(f'Thankyou for running! {client.user}')
    await tree.sync()

@tree.command(name="button", description="認証ボタンの表示")
async def panel_au(interaction: discord.Interaction,ロール:discord.Role,タイトル:str=None,説明:str=None):
    if タイトル==None:
        タイトル="こんにちは！"
    if 説明==None:
        説明="リンクボタンから登録して認証完了"
    try:
        if interaction.user.guild_permissions.administrator:
            ch = interaction.channel
            embed = discord.Embed(title=タイトル,description=説明,color=discord.Colour.blue())
            id=ロール.id
            button = discord.ui.Button(label="登録リンク", style=discord.ButtonStyle.primary, url=authurl+f"&state={interaction.guild_id},{id}")
            
            view = discord.ui.View()
            view.add_item(button)
            await interaction.response.send_message("made by .taka. thankyou for running!!!", ephemeral=True)
            try:
                await ch.send(embed = embed, view = view)
            except:
                await ch.send("メッセージの送信に失敗しました")
                return
        else:
            await interaction.response.send_message("管理者しか使えません", ephemeral=True)
            return    
    except:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)


@tree.command(name="call", description="認証したひと”全員”を追加する")
async def call(interaction: discord.Interaction,追加先のサーバーid:str=None,データサーバーid:str=None):
    try:
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("登録されたユーザーを追加中です...")
            if データサーバーid==None:
                useridj=open(ipath)
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
            for key, value in userid.items():
                rea=requests.put('https://discord.com/api/guilds/' + f"{guild_id}" + '/members/' + key, headers=head, json={"access_token": value})    
                if rea.status_code==201:
                    a=a+1
                elif rea.status_code==204:
                    b=b+1
                elif rea.status_code==403:
                    c=c+1
                elif rea.status_code==429:
                    e=e+1
                else:
                    d=d+1
            await interaction.channel.send(f"リクエストが終わりました\n{a}人を追加\n{b}人は既に追加されていて\n{c}人の情報が失効済み\n{e}回Too many request\n{d}人は不明なエラーです")
        else:
            await interaction.response.send_message("管理者しか使えません", ephemeral=True)
            return    
    except:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)


@tree.command(name="check", description="UserIDを使ってTokenを検索する")
async def check(interaction: discord.Interaction,ユーザーid:str):
    try:
        if interaction.user.guild_permissions.administrator:
            useridj=open(ipath)
            userid = json.load(useridj)
            try:
                token=(userid[f"{ユーザーid}"])
                await interaction.response.send_message(f"該当ユーザーのトークンは：{token}：です\nUserID：{ユーザーid}", ephemeral=False)

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
                await interaction.response.send_message(f"該当ユーザーの情報を削除しました\nUserID：{ユーザーid}", ephemeral=False)

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
client.run(BOTTOKEN)
