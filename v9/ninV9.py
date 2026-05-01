import discord
import json
import time
import os
import asyncio
from ninFlaskV8 import start
import v9path
from asyncEAGM import EAGM

client = discord.Client(intents = discord.Intents.default())
tree = discord.app_commands.CommandTree(client)

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "data")

usadata_path = os.path.join(data_dir, "usadata.json")
serverdata_folder_path = os.path.join(data_dir, "server_data")

BOTTOKEN = v9path.BOTTOKEN
CLIENT_ID = v9path.CLIENT_ID
REDIRECT_URI = v9path.REDIRECT_URI
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
    with open(os.path.join(serverdata_folder_path, f"{interaction.guild.id}.json"), "w") as f:
        json.dump({"role": str(ロール.id)}, f)

    try:
        await interaction.channel.send(view=view,embed=discord.Embed(title=タイトル, description=説明, color=discord.Colour.blue()))
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

    class CallStats:
        added: int = 0
        already_member: int = 0
        token_expired: int = 0
        server_full: int = 0
        rate_limited: int = 0
        refreshed: int = 0
        not_found: int = 0
        banned_from_server: int = 0
        limited_access: int = 0
        other_errors: int = 0

    stats = CallStats()
    user_ids_to_process = list(users_to_add.keys())

    for user_id in user_ids_to_process:
        access_token = all_user_data.get(user_id)

        if not access_token:
            if user_id in users_to_add:
                del users_to_add[user_id]
            continue
        
        result = await eagm.add_member(access_token, user_id, interaction.guild.id)

        if result.code == 400002 or result.code == 10004:
            embed = discord.Embed(title="あなたのサーバーは招待が停止されています", color=discord.Colour.red())
            await interaction.channel.send(embed=embed)
            return
        
        #if result.new_access_token:
        #    stats.refreshed += 1
        #
        #else:
        #    if result.need_refresh:
        #        result.status == 403

        if result.status == 201:
            stats.added += 1

        elif result.status == 204:
            stats.already_member += 1

        elif result.status == 403:
            if result.code == 10013:
                stats.not_found += 1
            
            elif result.code == 40007:
                stats.banned_from_server += 1

            elif result.code == 340015:
                stats.limited_access += 1

            else:
                stats.token_expired += 1
                    
        elif result.status == 429:
            stats.rate_limited += 1
            
        elif result.status == 400:
            stats.server_full += 1

        else:
            if result.code == 10013:
                stats.not_found += 1
            
            else:
                stats.other_errors += 1
                print(f"Unexpected result: {result}")
            
        if result.is_expired_access_token:
            del users_to_add[user_id]

        await asyncio.sleep(1)

    with open(target_user_path, 'w', encoding='utf-8') as f:
        json.dump(users_to_add, f, indent=4)


    with open(usadata_path, 'w', encoding='utf-8') as f:
        json.dump(all_user_data, f, indent=4)

    res = ""
    if stats.added:
        res = res + f"{stats.added}人を追加"
    else:
        res = res + "追加された人はいません"

    if stats.already_member:
        res = res + f"\n{stats.already_member}人は既に追加されていて"
    if stats.token_expired:
        res = res + f"\n{stats.token_expired}人の情報が失効済み"
    else:
        res = res + f"\n誰の情報も失効してません"

    if stats.server_full:
        res = res + f"\n{stats.server_full}人はもうサーバーに参加できません"
    if stats.not_found:
        res = res + f"\n{stats.not_found}人はアカウントが削除されているようです"
    if stats.banned_from_server:
        res = res + f"\n{stats.banned_from_server}人はこのサーバーからBANされています"
    if stats.limited_access:
        res = res + f"\n{stats.limited_access}人はアカウントが制限されています"
    if stats.other_errors:
        res = res + f"\n{stats.other_errors}人はその他のエラーです"
    if stats.rate_limited:
        res = res + f"\n{stats.rate_limited}回TooManyRequestsしました"
    #if stats.refreshed:
    #    res = res + f"\n{stats.refreshed}人の情報がリフレッシュされました"
    
    await interaction.channel.send(res)


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
        with open(usadata_path, "r", encoding="utf-8") as f:
            userdata = json.load(f)
    except:
        await interaction.response.send_message("登録されているユーザーデータはありません")
        return
    
    try:
        result = await eagm.add_member(userdata[ユーザーid], ユーザーid, interaction.guild.id)
        
        if result.status == 201:
            await interaction.response.send_message("該当のユーザーを追加しました")

        elif result.status == 204:
            await interaction.response.send_message("該当のユーザーは既に追加されています")

        elif result.status == 403:
            await interaction.response.send_message("該当ユーザーの保存情報は失効しています")

            del userdata[ユーザーid]
            with open(usadata_path, "w") as f:
                json.dump(userdata, f, indent=4)

        elif result.status == 400:
            await interaction.response.send_message("該当ユーザーはこれ以上サーバーに参加できません")

        elif result.status == 429:
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
        with open(usadata_path, "w") as f:
            json.dump(userdata, f, indent=4)

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
        with open(usadata_path, "r", encoding="utf-8") as f:            data = json.load(f)
        await interaction.response.send_message(f"{len(data)}人のデータが登録されています")
    except:
        await interaction.response.send_message("登録されているユーザーデータはありません")

start()
time.sleep(1)
client.run(BOTTOKEN)