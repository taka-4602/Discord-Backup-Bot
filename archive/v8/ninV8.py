import discord
import json
import time
import os
import asyncio
from ninFlaskV8 import start
import v8path
from asyncEAGM import EAGM

client = discord.Client(intents = discord.Intents.default())
tree = discord.app_commands.CommandTree(client)

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "data")

usadata_path = os.path.join(data_dir, "usadata.json")
serverdata_folder_path = os.path.join(data_dir, "serverdata")

BOTTOKEN = v8path.BOTTOKEN
CLIENT_ID = v8path.CLIENT_ID
REDIRECT_URI = v8path.REDIRECT_URI
authurl = f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=https%3A%2F%2F{REDIRECT_URI.split('/')[2]}%2F&scope=identify+guilds.join"

eagm = EAGM(bot_token=BOTTOKEN)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="認証ボタン"))
    print(f"Thankyou for running! {client.user}")
    await tree.sync()

@tree.command(name="button", description="認証ボタンの表示")
async def panel_au(interaction: discord.Interaction, ロール:discord.Role, タイトル:str="こんにちは！", 説明:str="リンクボタンから登録して認証完了"):
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
    json.dump({"role": str(ロール.id)}, open(os.path.join(serverdata_folder_path, f"{interaction.guild.id}.json"), "w"))

    try:
        await interaction.channel.send(view=view,embed=discord.Embed(title=タイトル,description=説明,color=discord.Colour.blue()))
    except Exception as e:
        print(e)


@tree.command(name="call", description='認証したユーザーをサーバーに追加します (管理者用)')
async def call(interaction: discord.Interaction, data_server_id: str = None):
    if not interaction.guild:
        await interaction.response.send_message("DMでは使用できません", ephemeral=True)
        return

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("このコマンドは管理者のみが使用できます", ephemeral=True)
        return

    try:
        with open(usadata_path, 'r', encoding='utf-8') as f:
            all_user_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        await interaction.response.send_message("登録されているユーザーデータはありません")
        return

    target_user_path = ""
    if not data_server_id:
        target_user_path = os.path.join(serverdata_folder_path, f"{interaction.guild_id}.json")

    elif data_server_id == "all":
        target_user_path = usadata_path

    else:
        target_user_path = os.path.join(serverdata_folder_path, f"{data_server_id}.json")

    try:
        with open(target_user_path, 'r', encoding='utf-8') as f:
            users_to_add = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        await interaction.response.send_message("登録されているユーザーデータはありません")
        return

    await interaction.response.send_message("登録されたユーザーを追加中です...")

    stats = {
        "added": 0,
        "already_joined": 0,
        "invalid_token": 0,
        "rate_limited": 0,
        "max_guilds_or_bad_request": 0,
        "unknown_error": 0
    }

    user_ids_to_process = list(users_to_add.keys())

    for user_id in user_ids_to_process:
        access_token = all_user_data.get(user_id)

        if not access_token:
            if user_id in users_to_add:
                del users_to_add[user_id]
            continue

        try:
            status_code = await eagm.add_member(
                access_token=access_token,
                user_id=user_id,
                guild_id=interaction.guild.id
            )

            if status_code == 201:
                stats["added"] += 1
            elif status_code == 204:
                stats["already_joined"] += 1
            elif status_code == 403:
                stats["invalid_token"] += 1
                if user_id in all_user_data:
                    del all_user_data[user_id]
                if user_id in users_to_add:
                    del users_to_add[user_id]
            elif status_code == 429:
                stats["rate_limited"] += 1
            elif status_code == 400:
                stats["max_guilds"] += 1
            else:
                stats["unknown_error"] += 1
                
        except Exception as e:
            print(e)
            stats["unknown_error"] += 1
        
        await asyncio.sleep(1) 

    with open(target_user_path, 'w', encoding='utf-8') as f:
        json.dump(users_to_add, f, indent=4)


    with open(usadata_path, 'w', encoding='utf-8') as f:
        json.dump(all_user_data, f, indent=4)

    await interaction.channel.send(f"リクエストが終わりました\n{stats['added']}人を追加\n{stats['already_joined']}人は既に追加されていて\n{stats['invalid_token']}人の情報が失効済み\n{stats['rate_limited']}回TooManyRequest\n{stats['max_guilds']}人はこれ以上サーバーに参加できません\n{stats['unknown_error']}人は不明なエラーです")


@tree.command(name="check", description="UserIDを使ってアクセストークンを検索する")
async def check(interaction: discord.Interaction,ユーザーid:str):
    if not interaction.guild:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("管理者しか使えません", ephemeral=True)
        return
    
    try:
        userdata = json.load(open(usadata_path))
    except:
        await interaction.response.send_message("登録されているユーザーデータはありません")
        return
    
    try:
        await interaction.response.send_message(f"該当ユーザーのトークンは```{userdata[ユーザーid]}```です\nUserID：```{ユーザーid}```")

    except:
        await interaction.response.send_message("ユーザー情報が見つかりませんでした")


@tree.command(name="request1", description="UserIDとトークンを使って1人リクエストする")
async def req1(interaction: discord.Interaction, ユーザーid:str):
    if not interaction.guild:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("管理者しか使えません", ephemeral=True)
        return
    try:
        userdata = json.load(open(usadata_path))
    except:
        await interaction.response.send_message("登録されているユーザーデータはありません")
        return
    try:
        addmember=eagm.add_member(access_token=userdata[ユーザーid],user_id=ユーザーid,guild_id=interaction.guild.id)
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
async def delk(interaction: discord.Interaction, ユーザーid:str):
    if not interaction.guild:
        await interaction.response.send_message("DMでは使えません", ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("管理者しか使えません", ephemeral=True)
        return
    
    try:
        userdata = json.load(open(usadata_path))
    except:
        await interaction.response.send_message("登録されているユーザーデータはありません")
        return
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
        await interaction.response.send_message("登録されているユーザーデータはありません")

start()
time.sleep(1)
client.run(BOTTOKEN)