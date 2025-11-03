import aiohttp
from typing import NamedTuple


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
        self.session = aiohttp.ClientSession(headers={"Content-Type": "application/json"})

    async def get_token(self, code:str):
        data = self.data
        data["grant_type"] = "authorization_code"
        data["code"] = code
        class GetTokenResponse(NamedTuple):
            access_token: str
            refresh_token: str

        async with self.session.post("https://discord.com/api/v10/oauth2/token", data=data, proxy=self.proxy) as response:
            response_json = await response.json()

        if not "guilds.join" in response_json["scope"]:
            raise EAGMError("スコープがおかしいです")

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

        async with self.session.get("https://discord.com/api/v10/users/@me", headers={"Authorization": f"Bearer {access_token}"}, proxy=self.proxy) as response:
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
        data = self.data
        data["grant_type"] = "refresh_token"
        data["refresh_token"] = refresh_token

        class RefreshResponse(NamedTuple):
            refreshed_access_token: str
            refreshed_refresh_token: str

        async with self.session.post("https://discord.com/api/v10/oauth2/token", data=data, proxy=self.proxy) as response:
            response_json = await response.json()
            if response.status > 300:
                raise EAGMError(response_json)

            return RefreshResponse(
                refreshed_access_token=response_json["access_token"],
                refreshed_refresh_token=response_json["refresh_token"]
            )

    async def add_member(self, access_token:str, user_id:int | str, guild_id:int | str):
        headers = {"Authorization": "Bot " + self.bot_token, "Content-Type": "application/json"}
        async with self.session.put("https://discord.com/api/guilds/" + str(guild_id) + "/members/" + str(user_id), headers=headers, json={"access_token": access_token}, proxy=self.proxy) as response:
            return response.status

    async def add_role(self, user_id: int | str, guild_id: int | str, role_id: int | str):
        headers = {"Authorization": "Bot " + self.bot_token, "Content-Type": "application/json"}
        async with self.session.put("https://discord.com/api/guilds/" + str(guild_id) + "/members/" + str(user_id) + "/roles/" + str(role_id), headers=headers, proxy=self.proxy) as response:
            return response.status