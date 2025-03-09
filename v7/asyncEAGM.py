import httpx

headers = {"Content-Type": "application/x-www-form-urlencoded"}

class EAGMError(Exception):
    pass
class EAGM:
    def __init__(self,bot_token:str=None,client_id:str=None,client_secret:str=None,redirect_uri:str=None,proxy:dict=None):
        self.proxy=proxy
        self.bot_token=bot_token
        self.data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }    

    async def get_token(self,code:str) -> dict:
        data=self.data
        data["grant_type"]="authorization_code"
        data["code"]=code
        async with httpx.AsyncClient(proxy=self.proxy) as session:
            gettoken = await session.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers)
            gettoken=gettoken.json()
            self.access_token=gettoken["access_token"]
            self.refresh_token=gettoken["refresh_token"]
            if not "guilds.join" in gettoken["scope"]:
                raise EAGMError("スコープがおかしいです")
            return gettoken
    
    async def get_user(self,access_token:str) -> dict:
        async with httpx.AsyncClient(proxy=self.proxy) as session:
            user = await session.get("https://discord.com/api/v10/users/@me", headers={"Authorization": f"Bearer {access_token}"})
            user=user.json()
            self.user_id=user["id"]
            self.username=user["username"]
            self.avatar=user["avatar"]
            self.global_name=user["global_name"]
            return user

    async def refresh(self,refresh_token:str):
        data=self.data
        data["grant_type"]="refresh_token"
        data["refresh_token"]=refresh_token
        async with httpx.AsyncClient(proxy=self.proxy) as session:
            refresh=await session.post("https://discord.com/api/v10/oauth2/token", data=data, headers=headers)
            if not refresh.status_code < 300:
                self.refreshed_access_token=None
                self.refreshed_refresh_token=None
                return refresh.status_code
            
            refresh=refresh.json()
            self.refreshed_access_token=refresh["access_token"]
            self.refreshed_refresh_token=refresh["refresh_token"]
            return refresh

    async def add_member(self,access_token:str,user_id:str,guild_id:str):
        head = {"Authorization": "Bot " + self.bot_token, "Content-Type": "application/json"}
        async with httpx.AsyncClient(proxy=self.proxy) as session:
            adgm=await session.put("https://discord.com/api/guilds/" + guild_id + "/members/" + user_id, headers=head, json={"access_token": access_token})
            return adgm.status_code
    
    async def add_role(self,user_id:str,guild_id:str,role_id:str):
        head = {"Authorization": "Bot " + self.bot_token, "Content-Type": "application/json"}
        async with httpx.AsyncClient(proxy=self.proxy) as session:
            role=await session.put("https://discord.com/api/guilds/" + guild_id + "/members/" + user_id + "/roles/" + role_id, headers=head)
            return role.status_code