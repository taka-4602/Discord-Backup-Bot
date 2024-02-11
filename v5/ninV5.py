import discord
import json
import time
from ninFlaskV5 import start
from call import callstart
import v5path
from EAGM import EAGM

intents = discord.Intents.default()
client = discord.Client(intents = intents)
tree = discord.app_commands.CommandTree(client)

ipath=v5path.ipath
ipath2=v5path.ipath2
BOTTOKEN=v5path.BOTTOKEN
authurl=v5path.authurl
eagm=EAGM(bot_token=BOTTOKEN)

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
                json.load(open(f"{ipath2}{interaction.guild.id}.json"))
            except:
                setup={}
                json.dump(setup,open(f"{ipath2}{interaction.guild.id}.json","w"))
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
    await interaction.response.send_message("登録されたユーザーを追加中です...")


@tree.command(name="check", description="UserIDを使ってアクセストークンを検索する")
async def check(interaction: discord.Interaction,ユーザーid:str):
    try:
        if interaction.user.guild_permissions.administrator:
            userid = json.load(open(ipath))
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
async def req1(interaction: discord.Interaction,ユーザーid:str):
    try:
        if interaction.user.guild_permissions.administrator:
            userid = json.load(open(ipath))
            try:
                token=(userid[f"{ユーザーid}"])
                addmember=eagm.add_member(access_token=token,user_id=ユーザーid,guild_id=str(interaction.guild_id))
                print(addmember)
                if addmember==201:
                    await interaction.response.send_message("該当のユーザーを追加しました")   
                elif addmember==204:
                    await interaction.response.send_message("該当のユーザーは既に追加されています")    
                elif addmember==403:
                    await interaction.response.send_message("該当ユーザーの保存情報は失効しています")
                elif addmember==400:
                    await interaction.response.send_message("該当ユーザーはこれ以上サーバーに参加できません")
                elif addmember==429:
                    await interaction.response.send_message("429レートリミットです")

                else:
                    await interaction.response.send_message("該当ユーザーの追加は失敗しました")
            except Exception as e:
                await interaction.response.send_message(f"ユーザー情報が見つかりませんでした\n{e}", ephemeral=False)
        else:
            await interaction.response.send_message("管理者しか使えません", ephemeral=True)
            return    
    except:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)


@tree.command(name="delkey", description="該当ユーザーの情報を削除する")
async def delk(interaction: discord.Interaction,ユーザーid:str):
    try:
        if interaction.user.guild_permissions.administrator:
            userid = json.load(open(ipath))
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
            userid = json.load(open(ipath))
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
