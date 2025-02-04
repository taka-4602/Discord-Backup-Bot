import discord
import json
import time
import asyncio
from ninFlaskV7 import start
import v7path
from asyncEAGM import EAGM

client = discord.Client(intents = discord.Intents.default())
tree = discord.app_commands.CommandTree(client)

usadata_path=v7path.usadata_path
serverdata_folder_path=v7path.serverdata_folder_path
BOTTOKEN=v7path.BOTTOKEN
authurl=v7path.authurl
eagm=EAGM(bot_token=BOTTOKEN)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="認証ボタン"))
    print(f"Thankyou for running! {client.user}")
    await tree.sync()

@tree.command(name="button", description="認証ボタンの表示")
async def panel_au(interaction: discord.Interaction,ロール:discord.Role,タイトル:str="こんにちは！",説明:str="リンクボタンから登録して認証完了"):
    if not interaction.guild:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("管理者しか使えません", ephemeral=True)
        return
    
    button = discord.ui.Button(label="登録リンク", style=discord.ButtonStyle.primary, url=authurl+f"&state={(hex(interaction.guild_id)).upper()[2:]}")
    view = discord.ui.View()
    view.add_item(button)
    await interaction.response.send_message("made by ```.taka.``` thankyou for running!", ephemeral=True)
    try:
        server_data=json.load(open(f"{serverdata_folder_path}{interaction.guild.id}.json"))
        server_data["role"]=str(ロール.id)
        json.dump(server_data,open(f"{serverdata_folder_path}{interaction.guild.id}.json","w"))
    except:
        json.dump({"role":str(ロール.id)},open(f"{serverdata_folder_path}{interaction.guild.id}.json","w"))
    try:
        await interaction.channel.send(view=view,embed=discord.Embed(title=タイトル,description=説明,color=discord.Colour.blue()))
    except Exception as e:
        print(e)


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
    await interaction.response.send_message("登録されたユーザーを追加中です...")
    for key in list(userdata.keys()):
        try:
            addmember=await eagm.add_member(access_token=alldata[key],user_id=key,guild_id=str(interaction.guild.id))
        except KeyError:
            del userdata[key]
            continue

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
        
        await asyncio.sleep(1)# <- TooManyRequest対策です！！おこのみの数値または必要ないなら消してください！(ふつうは1秒で充分です)

    if not データサーバーid:
        json.dump(userdata, open(f"{serverdata_folder_path}{interaction.guild_id}.json","w"))
        json.dump(alldata, open(usadata_path,"w"))
    elif データサーバーid=="all":
        json.dump(userdata, open(usadata_path,"w"))
    else:
        json.dump(userdata, open(f"{serverdata_folder_path}{データサーバーid}.json","w"))
        json.dump(alldata, open(usadata_path,"w"))

    await interaction.channel.send(f"リクエストが終わりました\n{a}人を追加\n{b}人は既に追加されていて\n{c}人の情報が失効済み\n{e}回TooManyRequest\n{f}人はこれ以上サーバーに参加できません\n{d}人は不明なエラーです")


@tree.command(name="check", description="UserIDを使ってアクセストークンを検索する")
async def check(interaction: discord.Interaction,ユーザーid:str):
    if not interaction.guild:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("管理者しか使えません", ephemeral=True)
        return
    
    userdata = json.load(open(usadata_path))
    try:
        await interaction.response.send_message(f"該当ユーザーのトークンは```{userdata[ユーザーid]}```です\nUserID：```{ユーザーid}```")

    except:
        await interaction.response.send_message("ユーザー情報が見つかりませんでした")


@tree.command(name="request1", description="UserIDとトークンを使って1人リクエストする")
async def req1(interaction: discord.Interaction,ユーザーid:str):
    if not interaction.guild:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("管理者しか使えません", ephemeral=True)
        return
    
    userdata = json.load(open(usadata_path))
    try:
        addmember=eagm.add_member(access_token=userdata[ユーザーid],user_id=ユーザーid,guild_id=str(interaction.guild_id))
        if addmember==201:
            await interaction.response.send_message("該当のユーザーを追加しました")   
        elif addmember==204:
            await interaction.response.send_message("該当のユーザーは既に追加されています")    
        elif addmember==403:
            await interaction.response.send_message("該当ユーザーの保存情報は失効しています")
            del userdata[ユーザーid]
            json.dump(userdata, open(usadata_path,"w"))
        elif addmember==400:
            await interaction.response.send_message("該当ユーザーはこれ以上サーバーに参加できません")
        elif addmember==404:
            await interaction.response.send_message("該当ユーザーのアカウントは削除されています")
        elif addmember==429:
            await interaction.response.send_message("429レートリミットです")

        else:
            await interaction.response.send_message("該当ユーザーの追加は失敗しました")
    except Exception as e:
        await interaction.response.send_message(f"ユーザー情報が見つかりませんでした\n{e}")


@tree.command(name="delkey", description="該当ユーザーの情報を削除する")
async def delk(interaction: discord.Interaction,ユーザーid:str):
    if not interaction.guild:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("管理者しか使えません", ephemeral=True)
        return
    
    userdata = json.load(open(usadata_path))
    try:
        del userdata[ユーザーid]
        json.dump(userdata, open(usadata_path,"w"))
        await interaction.response.send_message(f"該当ユーザーの情報を削除しました\nUserID：```{ユーザーid}```")

    except:
        await interaction.response.send_message("ユーザー情報が見つかりませんでした")


@tree.command(name="datacheck", description="登録人数の確認")
async def dck(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("管理者しか使えません", ephemeral=True)
        return
    
    try:
        await interaction.response.send_message(f"{len(json.load(open(usadata_path)))}人のデータが登録されています")
    except:
        await interaction.response.send_message("ファイルが使えなくなっています")

start()
time.sleep(1)
client.run(BOTTOKEN)