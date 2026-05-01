import aiohttp
from typing import NamedTuple
import asyncio

class EAGMError(Exception):
    pass
class EAGM:
    def __init__(self, bot_token:str=None, client_id:str=None, client_secret:str=None, redirect_uri:str=None, proxy:str=None):
        self.proxy = proxy
        self.bot_token = bot_token
        self.data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }

    async def get_token(self, code:str):
        data = self.data
        data["grant_type"] = "authorization_code"
        data["code"] = code
        class GetTokenResponse(NamedTuple):
            access_token: str
            refresh_token: str

        async with aiohttp.ClientSession(headers={"Content-Type": "application/x-www-form-urlencoded"}) as session:
            async with session.post("https://discord.com/api/v10/oauth2/token", data=data, proxy=self.proxy) as response:
                response_json = await response.json()

            try:
                if not "guilds.join" in response_json["scope"]:
                    raise EAGMError("スコープがおかしいです")

            except KeyError:
                raise EAGMError(response_json)

            return GetTokenResponse(
                access_token=response_json["access_token"],
                refresh_token=response_json["refresh_token"]
            )

    async def get_user(self, access_token: str):
        class GetUserResponse(NamedTuple):
            user_id: str
            username: str
            avatar: str
            global_name: str

        async with aiohttp.ClientSession(headers={"Authorization": f"Bearer {access_token}"}) as session:
            async with session.get("https://discord.com/api/v10/users/@me", headers={"Authorization": f"Bearer {access_token}"}, proxy=self.proxy) as response:
                response_json = await response.json()
                if response.status > 300:
                    raise EAGMError(response_json)

            return GetUserResponse(
                user_id=response_json["id"],
                username=response_json["username"],
                avatar=response_json["avatar"],
                global_name=response_json["global_name"]
            )


    async def refresh(self, refresh_token: str):
        """
        200 {'token_type': 'Bearer', 'access_token': 'MTQ0NjUwMjU3NTM3MjUwMTE1NA.fqZNkGhTbt6bez599V50UbJEBv3DjN', 'expires_in': 604800, 'refresh_token': 'yAdWnFz8UPgAQRRAGxi0wl4FYfzmww', 'scope': 'identify guilds.join'}

        400 {'error': 'invalid_grant'}
        """
        data = self.data
        data["grant_type"] = "refresh_token"
        data["refresh_token"] = refresh_token

        class RefreshResponse(NamedTuple):
            status: int
            access_token: str
            refresh_token: str
            message: str = None
            success: bool = False

        async with aiohttp.ClientSession(headers={"Content-Type": "application/x-www-form-urlencoded"}) as session:
            async with session.post("https://discord.com/api/v10/oauth2/token", data=data, proxy=self.proxy) as response:
                try:
                    response_json = await response.json()
                except:
                    response_json = {"error": "Failed to parse response"}

                if response.status == 429:
                    retry_after = response_json.get("retry_after", 0)
                    return RefreshResponse(
                        status=response.status,
                        access_token=None,
                        refresh_token=None,
                        message=f"Rate limited. Try again after {retry_after} seconds.",
                        success=False
                    )

                if response.status > 300:
                    message = response_json.get("error")
                    return RefreshResponse(
                        status=response.status,
                        access_token=None,
                        refresh_token=None,
                        message=message,
                        success=False
                    )


                return RefreshResponse(
                    status=response.status,
                    access_token=response_json["access_token"],
                    refresh_token=response_json["refresh_token"],
                    message=None,
                    success=True
                )

    async def add_member(self, access_token: str, user_id: int | str, guild_id: int | str, auto_refresh: bool = True, refresh_token: str = None):
        headers = {"Authorization": "Bot " + self.bot_token, "Content-Type": "application/json"}

        class AddMemberResponse(NamedTuple):
            status: int
            message: str
            code: int
            success: bool = False
            need_refresh: bool = False
            is_expired_access_token: bool = False
            new_access_token: str = None
            new_refresh_token: str = None

        async with aiohttp.ClientSession(headers=headers) as session:
            """
            201 {'avatar': None, 'banner': None, 'communication_disabled_until': None, 'flags': 0, 'joined_at': '2026-04-20T11:19:19.941198+00:00', 'nick': None, 'pending': False, 'premium_since': None, 'roles': [], 'unusual_dm_activity_until': None, 'collectibles': None, 'display_name_styles': None, 'user': {'id': '211565375689588737', 'username': '_.taka', 'avatar': '7f29eedb9d70caf14108969cb18dc190', 'discriminator': '0', 'public_flags': 0, 'flags': 0, 'banner': 'fd7351a5bda77af8f57d9d711f8ccb4e', 'accent_color': None, 'global_name': 'たか', 'avatar_decoration_data': {'asset': 'a_e90ebc0114e7bdc30353c8b11953ea41', 'sku_id': '1197344326133502032', 'expires_at': None}, 'collectibles': {'nameplate': {'sku_id': '1349849614286585866', 'asset': 'nameplates/nameplates/cityscape/', 'label': 'COLLECTIBLES_NAMEPLATES_CITYSCAPE_A11Y', 'palette': 'violet'}}, 'display_name_styles': None, 'banner_color': None, 'clan': {'identity_guild_id': '1403269573704290335', 'identity_enabled': True, 'tag': '学校行け', 'badge': '3df21ad31b154a436b8708114d8491e7'}, 'primary_guild': {'identity_guild_id': '1403269573704290335', 'identity_enabled': True, 'tag': '学校行け', 'badge': '3df21ad31b154a436b8708114d8491e7'}}, 'mute': False, 'deaf': False}
            204 No Content = すでにサーバーに参加している人

            ↑ success = True

            
            404 {'message': 'Unknown Guild', 'code': 10004} = Botがサーバーに参加していないGuild_ID
            403 {'message': 'Access to joining new servers has been limited for the user', 'code': 340015} = ユーザーが新しいサーバーへの参加を制限されている
            403 {'message': 'The user is banned from this guild.', 'code': 40007} = ユーザーがサーバーからBANされている

            ↑ is_expired_access_token = False

            403 {'message': 'Invalid OAuth2 access token', 'code': 50025} = アクセストークンが無効 -> これだけrefreshすればいい
            403 {'message': 'Unknown User', 'code': 10013} = ユーザーが存在しない
            403 {'message': 'Access to inviting new users through invite links has been limited for this guild', 'code': 400002} = サーバーが新規加入を制限している or 運営にされている
            50178 = invalid permissions <- 調査が必要
            10013 = Unknown User 404

            400 -> ユーザーが参加できるサーバーの上限
            """
            async with session.put(
                "https://discord.com/api/guilds/" + str(guild_id) + "/members/" + str(user_id),
                headers=headers,
                json={"access_token": access_token},
                proxy=self.proxy
            ) as response:
                
                success = False
                need_refresh = False
                is_expired_access_token = False
                new_access_token = None
                new_refresh_token = None
                if response.status == 201 or response.status == 204:
                    success = True
                
                try:
                    response_json = await response.json()
                except:
                    response_text = await response.text()
                    if response_text:
                        response_json = {"message": response_text, "code": None}
                    
                    else:
                        response_json = {"message": "", "code": None}

                if response.status == 429:
                    retry_after = response_json.get("retry_after", 0)
                    return AddMemberResponse(
                        status=response.status,
                        message="Rate limited. Try again later.",
                        code=retry_after,
                        success=False,
                        need_refresh=False,
                        is_expired_access_token=False,
                        new_access_token=None,
                        new_refresh_token=None
                    )

                code = response_json.get("code")
                message = response_json.get("message", "")

                if code == 50025:
                    need_refresh = True
                    is_expired_access_token = True
                
                if code in [10013]:
                    is_expired_access_token = True

                return AddMemberResponse(
                    status=response.status,
                    message=message,
                    code=code,
                    success=success,
                    need_refresh=need_refresh,
                    is_expired_access_token=is_expired_access_token,
                    new_access_token=new_access_token,
                    new_refresh_token=new_refresh_token
                )

    async def add_role(self, user_id: int | str, guild_id: int | str, role_id: int | str):
        headers = {"Authorization": "Bot " + self.bot_token, "Content-Type": "application/json"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.put("https://discord.com/api/guilds/" + str(guild_id) + "/members/" + str(user_id) + "/roles/" + str(role_id), headers=headers, proxy=self.proxy) as response:
                return response.status