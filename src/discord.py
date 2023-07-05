from tls_client import response
from time       import time
from typing     import Union
from base64     import b64encode
from json       import dumps, loads
from random     import choice

import urllib.parse
import httpx
import websocket

class Discord:
    def __init__(self, proxy, token, xsup, cli) -> None:
        if proxy:
            self.proxy = f"http://{proxy}"
        else:
            self.proxy = None
        self.session, self.headers, self.token, self.xsup = cli.session, cli.headers, token, xsup

    @staticmethod
    def latest_js():
        return (httpx.get(
                        "https://discord.com/app"
                        ).text.split(
                        '"></script><script src="/assets/'
                        )[2].split(
                        '" integrity'
                        )[0]
                    )
    @staticmethod
    def getBuildNum() -> str:
        req = httpx.get(
         f"https://discord.com/assets/{Discord.latest_js()}"
        )

        if req.status_code == 200:
            build_number = req.text.split('(t="')[1].split('")?t:"")')[0]

            return (
                 build_number
            )

    @staticmethod
    def getContextProperties(invite: str) -> Union[str, str]:
        req = httpx.get(
                f"https://discord.com/api/v9/invites/{invite}?with_counts=true&with_expiration=true"
            )
        req = req.json()
        g = req["guild"]["id"]
        c = req["channel"]["id"]
        t = req["channel"]["type"]

        return g, b64encode(dumps({"location":"Join Guild","location_guild_id":g,"location_channel_id":c,"location_channel_type":int(t)}).encode()).decode()

    def createDM(self, userID: str, guildID: str, channelID: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["authorization"] = self.token
        headers["referer"] = f"https://discord.com/channels/{guildID}/{channelID}"
        headers["x-context-properties"] = "e30="
        headers["x-super-properties"] = self.xsup

        js = {
            "recipients": [
                userID
            ]
        }

        req = self.session.post("https://discord.com/api/v9/users/@me/channels", headers=headers, proxy=self.proxy, json=js)

        return req.status_code == 200, req

    def closeDM(self, channelID: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["authorization"] = self.token
        headers["referer"] = "https://discord.com/channels/@me/" + channelID
        headers["x-super-properties"] = self.xsup

        req = self.session.delete("https://discord.com/api/v9/channels/"+channelID+"?silent=false", headers=headers, proxy=self.proxy)

        return req.status_code == 200, req

    def sendDM(self, channelID: str, message: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["authorization"] = self.token
        headers["referer"] = "https://discord.com/channels/@me/" + channelID
        headers["x-super-properties"] = self.xsup

        js = {
            "content": message,
            #"flags": 0,
            "nonce": ((int(time()) * 1000) - 1420070400000) * 4194304,
            "tts": False
        }

        req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/messages", headers=headers, proxy=self.proxy, json=js)

        return req.status_code == 200, req

    def leave(self, guildID: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["authorization"] = self.token

        payload = {
            "lurking": False
        }

        req = self.session.delete("https://discord.com/api/v9/users/@me/guilds/"+guildID, headers=headers, proxy=self.proxy, json=payload)

        return req.status_code == 200, req


    def join(self, invite: str, context: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["authorization"] = self.token
        headers["referer"] = "https://discord.com/invite/"+invite
        headers["x-context-properties"] = context
        headers["x-super-properties"] = self.xsup
        
        js = {
            "session_id": self.getSessionID(),
        }

        req = self.session.post(f"https://discord.com/api/v9/invites/{invite}", headers=headers, proxy=self.proxy, json=js)

        return req.status_code == 200, req

    def sendMessage(self, channelID: str, guildID: str, message: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        headers["referer"] = f"https://discord.com/channels/{guildID}/{channelID}"

        js = {
            "content": message, 
            "tts": "false"
        }

        req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/messages", headers=headers, proxy=self.proxy, json=js)

        return req.status_code == 200, req

    def friendRequest(self, username: str) -> Union[bool, response.Response]:
        username, discriminator = username.split("#")
        headers = self.headers

        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        headers["x-context-properties"] = "eyJsb2NhdGlvbiI6IkFkZCBGcmllbmQifQ=="
        headers["referer"] = "https://discord.com/channels/@me"

        js = {"username": username, "discriminator": int(discriminator)}

        req = self.session.post("https://discord.com/api/v9/users/@me/relationships", headers=headers, proxy=self.proxy, json=js)

        return req.status_code == 204, req

    def acceptRules(self, invite: str, guildID: str) -> Union[bool, response.Response]:
        headers = self.headers

        #headers["referer"] = "https://discord.com/channels/@me"
        headers["x-super-properties"] = self.xsup

        req = self.session.get(f"https://discord.com/api/v9/guilds/{guildID}/member-verification?with_guild=false&invite_code="+invite, headers=headers, proxy=self.proxy)
        js = req.json()
        payload = js
        if payload.get("form_fields") == None:
            return False, req


        for i in range(len(payload["form_fields"])):
            payload["form_fields"][i]["response"] = "true"


        headers["authorization"] = self.token

        req = self.session.put(f"https://discord.com/api/v9/guilds/{guildID}/requests/@me", headers=headers, proxy=self.proxy, json=payload)


        return req.status_code == 201, req

    def nickname(self, guildID: str, nickname: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup

        payload = {"nick": nickname}

        req = self.session.patch(f"https://discord.com/api/v9/guilds/{guildID}/members/@me" ,headers=headers, proxy=self.proxy, json=payload)

        return req.status_code == 200, req

    @staticmethod
    def joinVC(guildID: str, channelID: str, token: str, speaking: bool = False):
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        ws.send(dumps({"op": 2,"d": {"token": token, "properties": {"$os": "windows","$browser": "Discord","$device": "desktop"},"presence": {"status": choice(["online", "dnd", "idle"]),"since": 0,"activities": [],"afk": False}}}))
        ws.send(dumps({"op": 4,"d": {"guild_id": guildID,"channel_id": channelID, "self_mute": False,"self_deaf": False}}))
            
    @staticmethod
    def online(token: str):
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        ws.send(dumps({"op": 2,"d": {"token": token, "properties": {"$os": "windows","$browser": "Discord","$device": "desktop"},"presence": {"status": choice(["online", "dnd", "idle"]),"since": 0,"activities": [],"afk": False}}}))

    def getSessionID(self) -> str:
        ws = websocket.WebSocket()
        ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
        ws.send(dumps({"op": 2,"d": {"token": self.token, "properties": {"$os": "windows","$browser": "Discord","$device": "desktop"},"presence": {"status": choice(["online", "dnd", "idle"]),"since": 0,"activities": [],"afk": False}}}))

        for _ in range(10):
            js = loads(ws.recv())

            if js["d"].get("session_id"):
                return js["d"]["session_id"]
        
        return None


    def bypass(self, url: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["authorization"] = self.token

        js = {
            "authorize":   True,
		    "permissions": "0",
        }

        req = self.session.post(url, headers=headers, proxy=self.proxy, json=js)
        js = req.json()
        
        location = js["location"]

        headers = {
            "accept":          "*/*",
		    "accept-encoding": "gzip, deflate, br",
		    "accept-language": "en-US;q=0.9,en-GB;q=0.8",
		    "content-type":    "application/json",
		    "sec-fetch-dest":  "empty",
		    "sec-fetch-mode":  "cors",
		    "sec-fetch-site":  "same-origin",
		    "sec-ch-ua":       '"Not_A Brand";v="99", "Google Chrome";v="108", "Chromium";v="108"',
		    "user-agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }

        req = self.session.post(location, headers=headers, proxy=self.proxy)
        return req.status_code == 307, req

    def getButton(self, channelID: str, token: str):
        headers = self.headers

        headers["authorization"] = token

        req = self.session.get(f"https://discord.com/api/v9/channels/{channelID}/messages?limit=50", headers=headers, proxy=self.proxy)
        js = req.json()
        
        if req.status_code == 200:
            for i in js:
                if i.get("components") != []:
                    message_id = i["id"]
                    flags = i["flags"]
                        
                    custom_id = i["components"][0]["components"][0]["custom_id"]
                    typee = i["components"][0]["components"][0]["type"]
                    application_id = i["author"]["id"]
                    
                    if i["components"][0]["components"][0].get("options"):
                        options = i["components"][0]["components"][0]["options"]
                        return application_id, typee, custom_id, flags, message_id, options
                        
                    return application_id, typee, custom_id, flags, message_id, None

        return

    def button(self, application_id: str, typee: str, custom_id: str, flags: str, message_id: str, opt: str, channelID: str, guildID: str, value: str) -> Union[bool, response.Response]:
        sessionID = self.getSessionID()
        headers = self.headers

        headers["authorization"] = self.token

        js = {
            "application_id": application_id,
            "channel_id": channelID,
            "data": {
                "component_type": typee,
                "custom_id": custom_id,
            },
            "guild_id": guildID,
            "message_flags": flags,
            "message_id": message_id,
            "nonce": ((int(time()) * 1000) - 1420070400000) * 4194304,
            "type": 3,
            "session_id": sessionID,
        }
        
        if value:
            js["data"]["values"] = [value]


        headers["referer"] = "https://discord.com/channels/" + guildID + "/" + channelID

        headers["x-super-properties"] = self.xsup

        req = self.session.post("https://discord.com/api/v9/interactions", headers=headers, proxy=self.proxy, json=js)

        return req.status_code == 204, req

    def forum(self, guildID: str, channelID: str, title: str, message: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["referer"] = "https://discord.com/channels/" + guildID + "/" + channelID
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup

        js = {
            "applied_tags": [],
            "auto_archive_duration": 4320,
            "message": {
                "content": message,
            },
            "name": title,
        }

        req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/threads?use_nested_fields=true", headers=headers, proxy=self.proxy, json=js)

        return req.status_code == 201, req

    def getSubIDS(self) -> list:
        s = []

        headers = self.headers

        headers["referer"] = "https://discord.com/channels/@me"
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup

        try:
            req = self.session.get("https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers=self.headers, proxy=self.proxy).json()
        except Exception as e:
            return []

        for sub in req:
            s.append(sub["id"])

        return s

    def boost(self, guildID: str, ID: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["referer"] = "https://discord.com/channels/@me"
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup

        req = self.session.put(f"https://discord.com/api/v9/guilds/{guildID}/premium/subscriptions", headers=headers, proxy=self.proxy, json={"user_premium_guild_subscription_slot_ids": [ID]})

        return req.status_code == 201, req

    def getCustomEmoji(self, channelID: str, messageID: str) -> list:
        headers = self.headers

        headers["authorization"] = self.token
        
        emojis = []
        
        req = self.session.get(f"https://discord.com/api/v9/channels/{channelID}/messages?limit=50", headers=headers, proxy=self.proxy)
        js = req.json()
        
        if req.status_code == 200:
            for message in js:
                if message["id"] == messageID:
                    for reaction in message["reactions"]:
                        if reaction["emoji"]["id"]:
                            emojis.append((reaction["emoji"]["id"], reaction["emoji"]["name"]))
        
        return emojis
                
    def reaction(self, messageID: str, channelID: str, emoji: str, custom: bool = False) -> Union[bool, response.Response]:
        headers = self.headers

        #headers["referer"] = "https://discord.com/channels/@me/"+channelID
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup

        if custom:
            req = self.session.put(f"https://discord.com/api/v9/channels/{channelID}/messages/{messageID}/reactions/{emoji}/%40me?location=Message&type=0", headers=headers, proxy=self.proxy)
        else:
            req = self.session.put(f"https://discord.com/api/v9/channels/{channelID}/messages/{messageID}/reactions/{urllib.parse.quote(emoji)}/%40me?locat13on=Message&burst=false", headers=headers, proxy=self.proxy)

        return req.status_code == 204, req

    def threads(self, channelID: str, guildID: str, title: str) -> Union[bool, response.Response]:
        headers = self.headers

        headers["referer"] = "https://discord.com/channels/" + guildID + "/" + channelID
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup

        js = {
            "applied_tags": [],
            "auto_archive_duration": 4320,
            "name": title,
            "type": 11,
        }

        req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/threads", headers=headers, proxy=self.proxy, json=js)

        return req.status_code == 201, req

    def check(self) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        
        req = self.session.get("https://discord.com/api/v9/users/@me/settings", headers=headers, proxy=self.proxy)

        return req.status_code == 200, req

    @staticmethod
    def getReportingGuildMenu(token: str):
        headers = {}
        
        headers["authorization"] = token
        
        return httpx.get("https://discord.com/api/v9/reporting/menu/guild", headers=headers).json()
    
    def report(self, breadcrumbs: list, guild_id: str, data: dict) -> Union[bool, response.Response]:
        headers = self.headers
        
        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup
        
        js = {
            **data,
            "guild_id": guild_id,
            "breadcrumbs": breadcrumbs,
            "elements": {},
            "name": "guild",
            "guild_id": guild_id,
        }
        
        req = self.session.post("https://discord.com/api/v9/reporting/guild", headers=headers, proxy=self.proxy, json=js)
        return req.status_code == 200, req
    
    def changeAvatar(self, pfp: bytes):
        headers = self.headers
        
        headers["authorization"] = self.token
        
        data = b64encode(pfp)
        
        js = {
            "avatar": f"data:image/png;base64,{(data.decode('utf-8'))}"
        }
        
        req = self.session.patch("https://discord.com/api/v9/users/@me", headers=headers, proxy=self.proxy, json=js)
        return req.status_code == 200, req

    def getSoundboardDefaultSounds(self):
        headers = self.headers

        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup

        req = self.session.get("https://discord.com/api/v9/soundboard-default-sounds", headers=headers, proxy=self.proxy)

        return req.status_code == 200, req

    def sendSoundEffect(self, channelID: str, data: dict):
        headers = self.headers

        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup

        req = self.session.post(f"https://discord.com/api/v9/channels/{channelID}/voice-channel-effects", headers=headers, json=data, proxy=self.proxy)
        return req.status_code == 204, req

    def changeDisplayName(self, name: str):
        headers = self.headers

        headers["authorization"] = self.token
        headers["x-super-properties"] = self.xsup

        js = {
            "global_name": name
        }

        req = self.session.patch(f"https://discord.com/api/v9/users/@me", headers=headers, json=js, proxy=self.proxy)
        return req.status_code == 200, req
    
#🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣
