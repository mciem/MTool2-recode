from src.client  import Client
from src.console import Console
from src.discord import Discord
from src.scraper import DiscordSocket
from src.utils   import *

from json      import loads
from itertools import cycle
from unidecode import unidecode
from base64    import b64decode

import threading
import random
import time
import sys

#🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣
class MTool2:
    def __init__(self) -> None:
        self.cns  = Console()
        self.cli  = Client()

        with open("config.json", "r") as f:
            data = loads(f.read())

            self.use_proxy = data["use_proxy"]
            if data["show_discord_RPC"]:
                presence()
                self.cns.info("Started Discord RPC!")

        with open("data/tokens.txt", "r") as f:
            self.tokens = f.read().splitlines()

            if self.tokens == []:
                self.cns.error("Put your tokens -> data/tokens.txt")
                sys.exit(1)
            else:
                self.cns.info(f"{len(self.tokens)} tokens loaded!")

        if self.use_proxy:
            with open("data/proxies.txt", "r") as f:
                data = f.read().splitlines()

                if data == []:
                    self.cns.error("0 proxies loaded, running proxyless")
                    self.use_proxy = False
                else:
                    self.cns.info(f"{len(data)} proxies loaded!")
            
                self.proxies = cycle(data)

        build_num = Discord.getBuildNum()
        self.cns.info(f"Build Number -> {str(build_num)}")

        self.xsuper = XSuperProperties(build_num)
        print(self.xsuper)
        
        time.sleep(3)

    
    def getProxy(self):
        if self.use_proxy:
            return next(self.proxies)
        return None

    def getTokenIDS(self):
        ids = []
        for token in self.tokens:
            idd= b64decode(token[:24].encode()).decode()
            ids.append(idd)

        return ids

    def spammerDM(self, message: str, guildid: str, channelid: str, userid: str, token: str):
        dc = Discord(self.getProxy(), token, self.xsuper, self.cli)

        st, resp = dc.createDM(userid, guildid, channelid)
        js = resp.json()
        if st:
            cr = js["id"]
            self.cns.success(f"Created channel -> {cr}")
        else:
            cr = js["message"]
            self.cns.info(f"Failed to create channel -> {cr}")
            return

        while True:
            try:
                st, resp = dc.sendDM(cr, message)
            except Exception as e:
                self.cns.error(f"-> {str(e)}")

            if st:
                self.cns.success(f"DM sent -> {message}")
            else:
                a = resp.json()
                self.cns.info(f"Failed to send DM -> {a}")

                match resp.status_code:
                    case 400:
                        self.cns.info(f"Failed to send DM -> captcha")
                        return
                    case 429:
                        self.cns.info(f"Failed to send DM -> ratelimit")
                        handleRatelimit(a)
                    case _:
                        self.cns.info(f"Failed to send DM -> {a}")


    def massDM(self, message: str, guildid: str, channelid: str, close: bool, IDs: list, tokens: list):
        IDsSave = IDs.copy()

        x = 0
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)

            while True:
                try:
                    st, resp = dc.createDM(IDs[x], guildid, channelid)
                    js = resp.json()
                except Exception as e:
                    self.cns.error(f"-> {str(e)}")
                    continue
                if st:
                    cr = js["id"]
                    self.cns.info(f"Created channel -> {cr}")
                else:
                    cr = js["message"]
                    self.cns.info(f"Failed to create channel -> {cr}")
                    continue

                st, resp = dc.sendDM(cr, message)

                if st:
                    self.cns.success(f"DM sent to {IDs[x]}")
                    IDsSave.remove(IDs[x])
                else:
                    a = resp.text        
                    
                    match resp.status_code:
                        case 403:
                            self.cns.info(f"Failed to send DM -> opening dms too fast")
                            time.sleep(120)
                        case 429:
                            self.cns.info(f"Failed to send DM -> ratelimit")
                            time.sleep(30)
                        case _:
                            self.cns.info(f"Failed to send DM -> {a}")
                            

                if close:
                    st, resp = dc.closeDM(cr)
                    if st:
                        self.cns.info(f"DM closed")
                    else:
                        a = resp.text
                        self.cns.info(f"Failed to close DM -> {a}")
                x += 1

                time.sleep(5)
        
        with open(f"data/scraped/{guildid}.txt", "w") as f:
            data = ""
            for id in IDsSave:
                data += id + "\n"

            f.write(data)

    def scrape(self, token: str, channelID: str, guildID: str):
        token_ids = self.getTokenIDS()

        soc = DiscordSocket(token, guildID, channelID)
        IDs = soc.run()

        with open(f"data/scraped/{guildID}.txt", "w+") as f:
            data = ""
            for key, values in IDs.items():
                if key in token_ids:
                    continue
                data += key + "\n"

            f.write(data)

        with open("data/scraped/names.txt", "a+", encoding="latin-1") as f:
            data = ""
            for key, values in IDs.items():
                data += unidecode(values["tag"]) + "\n"

            f.write(data)


        self.cns.success(f"Scraped: {len(IDs)} IDs")

        return IDs

    def join(self, invite: str, context: str, tokens: list, guildID: str = ""):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)

            try:
                st, resp = dc.join(invite, context)
            except Exception as e:
                self.cns.error(f"-> {str(e)}")
                continue

            if st:
                js = resp.json()
                self.cns.success(f"Joined -> {invite}")
                
                if guildID != "":
                    st, resp = dc.acceptRules(invite, guildID)
                    if st:
                        self.cns.success(f"Bypassed rules -> {invite}")
                    else:
                        js = resp.json()
                        self.cns.info(f"Failed to bypass rules -> {js}")
            else:
                js = resp.json()

                match resp.status_code:
                    case 400:
                        self.cns.info("Failed to join -> captcha")
                    case 429:
                        self.cns.info("Failed to join -> ratelimit")
                        handleRatelimit(js)
                    case _:
                        self.cns.info(f"Failed to join -> {js}")

    def leave(self, guildID: str, tokens: list):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            try:
                st, resp = dc.leave(guildID)
            except Exception as e:
                self.cns.error(f"-> {str(e)}")
                continue

            if st:
                self.cns.success(f"Left -> {guildID}")
            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info("Failed to leave -> ratelimit")
                    case _:
                        self.cns.info(f"Failed to leave -> {js}")

    def friend(self, username: str, tokens: list):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            try:
                st, resp = dc.friendRequest(username)
            except Exception as e:
                self.cns.error(f"-> {str(e)}")
                continue

            if st:
                self.cns.success("Sent friend request!")
            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info("Failed to send friend req -> ratelimit")
                    case _:
                        self.cns.info(f"Failed to send friend req  -> {js}")

    def spammer(self, channelID: str, guildID: str, message: str, token: str, ids: list = [], pings: int = 0):
        spl = channelID.split(",")
        dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
        random.shuffle(ids)
        ids = cycle(ids)
        
        while True:
            msg = message
            for _ in range(pings):
                msg += f" <@{next(ids)}>"

            try:
                st, resp = dc.sendMessage(random.choice(spl), guildID, msg)
            except Exception as e:
                self.cns.error(f"-> {str(e)}")
                continue

            if st:
                self.cns.success("Sent message!")
            else:
                js = resp.json()
                match resp.status_code:
                    case 400:
                        print(js)
                        self.cns.info("Failed to send message -> invalid body")
                    case 401:
                        self.cns.info("Failed to send message -> invalid token")
                    case 403:
                        self.cns.info("Failed to send message -> missing access")
                    case 404:
                        self.cns.info("Failed to send message -> channel not found")
                    case 429:
                        self.cns.info("Failed to send message -> ratelimit")
                        handleRatelimit(js)
                        continue
                    case _:
                        self.cns.info(f"Failed to send message  -> {js}")
                        continue
                    
                return


    def checker(self, tokens: list):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            try:
                st, resp = dc.check()
            except Exception as e:
                self.cns.error(f"-> {str(e)}")
                continue

            if st:
                self.cns.info(f"Unlocked -> {token[:24]}")
                self.v.append(token)
            else:
                m = resp.json()["message"]
                if m == "401: Unauthorized":
                    self.cns.info(f"Invalid -> {token[:24]}")
                else:
                    self.cns.info(f"Locked -> {token[:24]}")

    def verifyBypass(self, url: str, tokens: list):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            try:
                st, resp = dc.bypass(url)
            except Exception as e:
                self.cns.error(f"-> {str(e)}")
                continue

            if st:
                self.cns.success(f"Verified -> {token[:24]}")
            else:
                js = resp.json()
                match resp.status_code:
                    case 429:
                        self.cns.info("Failed to verify -> ratelimit")
                    case _:
                        self.cns.info(f"Failed to verify  -> {js}")

    def button(self, messageshit: list, channelID: str, guildID: str, amount: int, tokens: list, opt: str):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)

            for _ in range(amount):
                try:
                    st, resp = dc.button(*messageshit, channelID, guildID, opt)
                except Exception as e:
                    self.cns.error(f"-> {str(e)}")
                    continue

                if st:
                    js = resp.text
                    self.cns.success(f"Button clicked")
                else:
                    js = resp.json()
                    match resp.status_code:
                        case 429:
                            self.cns.info("Failed to click button -> ratelimit")
                            handleRatelimit(js)
                            self.button(messageshit, channelID, guildID, amount, tokens, opt)
                        case _:
                            self.cns.info(f"Failed to click button  -> {js}")

    def forumFlooder(self, channelID: str, guildID: str, message: str, title: str, tokens: list):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)

            while True:
                try:
                    st, resp = dc.forum(guildID, channelID, title, message)
                except Exception as e:
                    self.cns.error(f"-> {str(e)}")
                    continue

                if st:
                    self.cns.success(f"Created post!")
                else:
                    js = resp.json()
                    match resp.status_code:
                        case 429:
                            self.cns.info("Failed to create post -> ratelimit")
                            handleRatelimit(js)
                        case _:
                            self.cns.info(f"Failed to create post -> {js}")

    def boostServer(self, guildID: str, tokens: list):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            subs = dc.getSubIDS()

            if subs == []:
                self.cns.info(f"Token has no boosts -> {token[:24]}")

            for sub in subs:
                try:
                    st, resp = dc.boost(guildID, sub)
                except Exception as e:
                    self.cns.error(f"-> {str(e)}")
                    continue

                if st:
                    self.cns.success("Boosted server!")
                else:
                    js = resp.json()
                    match resp.status_code:
                        case 429:
                            self.cns.info("Failed to boost server -> ratelimit")
                        case _:
                            self.cns.info(f"Failed to boost server -> {js}")

    def reactionAdder(self, messageID: str, channelID: str, emoji: str, tokens: list, multiple = False, custom = False):
        if multiple:
            emoji = ["😂", "🥲","🥰", "😘", "😍", "🔥", "💯", "💀", "🥵", "😈", "🤯", "🤗", "🤫", "😼"]
            random.shuffle(emoji)
        else:
            emoji = [emoji]
        
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            
            for emoj in emoji:
                try:
                    st, resp = dc.reaction(messageID, channelID, emoj, custom)
                except Exception as e:
                        self.cns.error(f"-> {str(e)}")
                        continue

                if st:
                    self.cns.success("Added reaction!")
                else:
                    js = resp.json()
                    match resp.status_code:
                        case 400:
                            self.cns.info("Failed to add reaction -> invalid body")
                        case 401:
                            self.cns.info("Failed to add reaction -> invalid token")
                        case 403:
                            self.cns.info("Failed to add reaction -> missing access")
                        case 404:
                            self.cns.info("Failed to add reaction -> channel/message not found")
                        case 429:
                            self.cns.info("Failed to add reaction -> ratelimit")
                            handleRatelimit(js)
                            continue
                        case _:
                            self.cns.info(f"Failed to add reaction   -> {js}")
                            continue

    def threads(self, channelID: str, guildID: str, title: str, tokens: list, message: str = ""):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            try:
                st, resp = dc.threads(channelID, guildID, title)
            except Exception as e:
                    self.cns.error(f"-> {str(e)}")
                    continue

            if st:
                self.cns.success("Created thread!")
                idd = resp.json()["id"]

                if message != "":
                    x = threading.Thread(target=self.spammer, args=(idd, guildID, message,token,))
                    self.threadss.append(x)
                    x.start()

            else:
                js = resp.json()
                match resp.status_code:
                        case 429:
                            self.cns.info("Failed to create thread -> ratelimit")
                        case _:
                            self.cns.info(f"Failed to create thread -> {js}")

    def nickname(self, guildID: str, nickname: str, tokens: list):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            try:
                st, resp = dc.nickname(guildID, nickname)
            except Exception as e:
                    self.cns.error(f"-> {str(e)}")
                    continue

            if st:
                self.cns.success("Nickname changed!")
            else:
                js = resp.json()
                match resp.status_code:
                        case 429:
                            self.cns.info("Failed to change nickname -> ratelimit")
                        case _:
                            self.cns.info(f"Failed to change nickname -> {js}")

    def report(self, breadcrumbs: list, guild_id: str, data: dict, amount: int, tokens: list):
        for token in tokens:
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            for _ in range(amount):
                try:
                    st, resp = dc.report(breadcrumbs, guild_id, data)
                except Exception as e:
                        self.cns.error(f"-> {str(e)}")
                        continue
                
                js = resp.json()
                
                if st:
                    report_id = js["report_id"]
                    self.cns.success(f"Reported server -> {report_id}")
                else:
                    match resp.status_code:
                        case 429:
                            self.cns.info("Failed to report server -> ratelimit")
                            handleRatelimit(js)
                        case _:
                            self.cns.info(f"Failed to report server -> {js}")
    
    def avatar(self, avatar: bytes, tokens: list):
        for token in tokens:
            Discord.online(token)
            
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            try:
                st, resp = dc.changeAvatar(avatar)
            except Exception as e:
                    self.cns.error(f"-> {str(e)}")
                    continue

            if st:
                self.cns.success("Avatar changed!")
            else:
                js = resp.json()
                match resp.status_code:
                        case 429:
                            self.cns.info("Failed to change avatar -> ratelimit")
                        case _:
                            self.cns.info(f"Failed to change avatar -> {js}")
    
    def soundboard(self, channelID: str, guildID: str, sound: dict, tokens: list):
        for token in tokens:
            Discord.joinVC(guildID, channelID, token)
            time.sleep(1)
            
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            while True:
                try:
                    st, resp = dc.sendSoundEffect(channelID, sound)
                except Exception as e:
                        self.cns.error(f"-> {str(e)}")
                        continue

                if st:
                    self.cns.success("Used soundboard effect!")
                else:
                    js = resp.json()
                    match resp.status_code:
                            case 429:
                                self.cns.info("Failed to use soundboard effect -> ratelimit")
                            case _:
                                self.cns.info(f"Failed to use soundboard effect -> {js}")
    
    def displayName(self, name: str, tokens: list):
        for token in tokens:            
            dc = Discord(self.getProxy(), token, self.xsuper, self.cli)
            try:
                st, resp = dc.changeDisplayName(name)
            except Exception as e:
                    self.cns.error(f"-> {str(e)}")
                    continue

            if st:
                self.cns.success(f"Changed Name -> {name}")
            else:
                js = resp.json()
                match resp.status_code:
                        case 429:
                            self.cns.success("Failed to change name -> ratelimit")
                        case _:
                            self.cns.info(f"Failed to change name -> {js}")
    
    '''def customScripts(self, script: str):
        functions = {
            "JOIN": self.join,
            "SCRAPER": self.scrape,
            "LEAVE": self.leave,
            "SPAM": self.spammer,
            "FRIEND": self.friend,
            "SPAMDM": self.spammerDM,
            #"VCJOIN": Discord.joinVC,
            #"ONLINE": Discord.online,
            "NICKNAME": self.nickname,
            "REPORT": self.report,
            "AVATAR": self.avatar,
            "SOUNDBOARD": self.soundboard,
            
            
        }'''
    
    def split_list(self, a, n):
        k, m = divmod(len(a), n)
        return list(a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

    def start(self):
        while True:
            self.cns.clear()
            self.cns.logo()
            self.cns.options()

            print()
            opt = int(self.cns.input("Option"))

            match opt:
                case 1:
                    
                    mes = self.cns.input("Message")
                    g = self.cns.input("Guild ID")
                    c = self.cns.input("Channel ID")
                    close = self.cns.input("Close DM (Y/N)")
                    if close == "Y" or close == "y":
                        cl = True
                    else:
                        cl = False
                        
                    with open(f"data/scraped/{g}.txt", "r") as f:
                        IDs = f.read().splitlines()
                    
                    calc = len(IDs) // len(self.tokens)
                
                    if calc < 1:
                        calc = len(self.tokens)
                    
                    if calc > len(self.tokens):
                        calc = len(self.tokens)
                    

                    ids = self.split_list(IDs, calc)
                    tokens = self.split_list(self.tokens, calc)
                    
                    threads = []
                    asd = 0
                    for x in tokens:
                        a = threading.Thread(target=self.massDM, args=(mes, g, c, cl, ids[asd], x))
                        threads.append(a)
                        a.start()
                        asd += 1
                    
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)

                    time.sleep(3)
                
                case 2:
                    tkn = self.cns.input("Token")
                    g = self.cns.input("Guild ID")
                    c = self.cns.input("Channel ID")
                    self.scrape(tkn, c, g)

                    time.sleep(3)
                
                case 3:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    inv = self.cns.input(f"Invite")
                    byp = self.cns.input("Bypass rules (Y/N)")
                    delay = float(self.cns.input("Delay (s)"))
                    
                    try:
                        guildID, context = Discord.getContextProperties(inv)
                    except Exception as e:
                        self.cns.error(f"-> {str(e)}")
                    
                    if delay == 0:
                        tokens = self.split_list(self.tokens, int(threads))
                        
                        threads = []
                        for x in tokens:
                            if byp == "Y" or byp == "y":
                                a = threading.Thread(target=self.join, args=(inv, context, x, guildID))
                            else:
                                a = threading.Thread(target=self.join, args=(inv, context, x))
                            
                            a.start()
                            threads.append(a)
                            
                        
                        while threads != []:
                            for x in threads:
                                if not x.is_alive():
                                    x.join()
                                    threads.remove(x)
                    else:
                        for token in self.tokens:
                            self.join(inv, context, [token])
                            time.sleep(delay)
                    
                    time.sleep(3)
                
                case 4:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    g = self.cns.input("Guild ID")
                    
                    tokens = self.split_list(self.tokens, int(threads))
                    
                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.leave, args=(g, x))
                        threads.append(a)
                        a.start()
                    
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                
                case 5:
                    self.cns.clear()
                    self.cns.logo()
                    self.cns.spammer_options()
                    
                    print()
                    opt = int(self.cns.input("Option"))
                    
                    match opt:
                        case 1:
                            message = self.cns.input("Message")
                            c = self.cns.input("Channel IDs (separated with commas)")
                            g = self.cns.input("Guild ID")
                            mp = self.cns.input("Mass Ping (Y/N)")
                            if mp == "Y" or mp == "y":
                                with open(f"data/scraped/{g}.txt", "r") as f:
                                    ids = f.read().splitlines()
                                mp = True
                                pings = int(self.cns.input("Amount of pings per message"))
                            else:
                                ids = []
                                pings = 0
                                mp = False
                            
                            threads = []
                            for x in self.tokens:
                                a = threading.Thread(target=self.spammer, args=(c,g, message, x, ids, pings))
                                threads.append(a)
                                a.start()
                        
                            while threads != []:
                                for x in threads:
                                    if not x.is_alive():
                                        x.join()
                                        threads.remove(x)
                        
                            time.sleep(3)

                        case 2:
                            threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                            title = self.cns.input("Title")
                            g = self.cns.input("Guild ID")
                            c = self.cns.input("Channel ID")
                            autospam = self.cns.input("Spam in thread (Y/N)")
                            
                            if autospam == "Y" or autospam == "y":
                                message = self.cns.input("Message")
                            else:
                                message = ""
                            
                            tokens = self.split_list(self.tokens, int(threads))
                            
                            self.threadss = []
                            for x in tokens:
                                a = threading.Thread(target=self.threads, args=(c, g, title, x, message))
                                self.threadss.append(a)
                                a.start()

                            time.sleep(1)
                            
                            while self.threadss != []:
                                for x in self.threadss:
                                    if not x.is_alive():
                                        x.join()
                                        self.threadss.remove(x)
                        
                            time.sleep(3)
                        
                        case 3:
                            threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                            username = self.cns.input("Username (someone#0000)")
                            
                            tokens = self.split_list(self.tokens, int(threads))
                            
                            threads = []
                            for x in tokens:
                                a = threading.Thread(target=self.friend, args=(username, x))
                                threads.append(a)
                                a.start()
                        
                            while threads != []:
                                for x in threads:
                                    if not x.is_alive():
                                        x.join()
                                        threads.remove(x)
                        
                            time.sleep(3)
                        
                        case 4:
                            message = self.cns.input("Message")
                            u = self.cns.input("User ID")
                            g = self.cns.input("Guild ID")
                            c = self.cns.input("Channel ID")
                            
                            threads = []
                            for x in self.tokens:
                                a = threading.Thread(target=self.spammerDM, args=(message, g, c, u, x))
                                threads.append(a)
                                a.start()
                            
                            while threads != []:
                                for x in threads:
                                    if not x.is_alive():
                                        x.join()
                                        threads.remove(x)
                        
                            time.sleep(3)

                case 6:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")

                    tokens = self.split_list(self.tokens, int(threads))
                    
                    self.v = []
                    
                    threads = []
                    f = open("data/tokens.txt", "w")
                    f.close()

                    for x in tokens:
                        a = threading.Thread(target=self.checker, args=(x,))
                        threads.append(a)
                        a.start()
                        
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    f = open("data/tokens.txt", "a+")
                    for token in self.v:
                        f.write(token+"\n")
                    
                    f.close()
                    
                    time.sleep(3)
                
                case 7:
                    g = self.cns.input("Guild ID")
                    c = self.cns.input("Channel ID")

                    for token in self.tokens:
                        Discord.joinVC(g, c, token)
                        self.cns.info(f"Joined VC with {token}")
                    
                    time.sleep(3)
                
                case 8:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    n = self.cns.input("Nickname")
                    g = self.cns.input("Guild ID")
                    
                    tokens = self.split_list(self.tokens, int(threads))

                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.nickname, args=(g, n, x,))
                        threads.append(a)
                        a.start()
                        
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                
                case 9:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    u = self.cns.input("URL")                
                    tokens = self.split_list(self.tokens, int(threads))

                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.verifyBypass, args=(u, x,))
                        threads.append(a)
                        a.start()
                        
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                
                case 10:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    c = self.cns.input("Channel ID")
                    g = self.cns.input("Guild ID")                    
                    am = int(self.cns.input("Amount per token"))

                    tokens = self.split_list(self.tokens, int(threads))
                    
                    tkn = random.choice(self.tokens)
                    dc = Discord(self.getProxy(), tkn, self.xsuper, self.cli)
                    messageshit = dc.getButton(c, tkn)
                    
                    while messageshit == None:
                        self.cns.info(f"Couldn't get button on {tkn[:24]}...")
                        tkn = random.choice(self.tokens)
                        dc = Discord(self.getProxy(), tkn, self.xsuper, self.cli)
                        messageshit = dc.getButton(c, tkn)
                    
                    self.cns.success(f"Obtained button data -> {messageshit}")
                    
                    options = messageshit[5]
                        
                    if options:
                        opt = self.cns.ticketOptions(options)
                    else:
                        opt = None
                    
                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.button, args=(messageshit, c, g, am, x,opt))
                        threads.append(a)
                        a.start()
                        
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                
                case 11:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    c = self.cns.input("Channel ID")
                    g = self.cns.input("Guild ID")    
                    title = self.cns.input("Title")
                    message = self.cns.input("Message")
                    
                    tokens = self.split_list(self.tokens, int(threads))
                    
                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.forumFlooder, args=(c, g, message,title, x,))
                        threads.append(a)
                        a.start()
                        
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                
                case 12:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    g = self.cns.input("Guild ID")

                    tokens = self.split_list(self.tokens, int(threads))
                    
                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.boostServer, args=(g,x ,))
                        threads.append(a)
                        a.start()
                        
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                
                case 13:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    message = self.cns.input("Message ID")
                    c = self.cns.input("Channel ID")
                    cus = self.cns.input("Custom Emoji (y/n)")
                    if cus == "y":
                        mul = False
                        cus = True
                        
                        dc = Discord(self.getProxy(), random.choice(self.tokens), self.xsuper, self.cli)
                        emojis = dc.getCustomEmoji(c, message)
                        
                        while emojis == []:
                            dc = Discord(self.getProxy(), random.choice(self.tokens), self.xsuper, self.cli)
                            emojis = dc.getCustomEmoji(c, message)
                            
                        names = [y for _, y in emojis]
                        
                        emoji = self.cns.input(f"Emoji ({','.join(names)})")
                        
                        for x, y in emojis:
                            if y == emoji:
                                emoji = f"{y}%3A{x}"
                    else:
                        cus = False
                        
                        m = self.cns.input("Multilple Emojis (y/n)")
                        if m == "y":
                            mul = True
                            emoji = ""
                        else:
                            mul = False
                            emoji = self.cns.input("Emoji")
                    
                    tokens = self.split_list(self.tokens, int(threads))
                    
                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.reactionAdder, args=(message, c, emoji, x, mul, cus))
                        threads.append(a)
                        a.start()
                        
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                
                case 14:
                    for token in self.tokens:
                        Discord.online(token)
                        self.cns.info(f"Online -> {token[:24]}...")

                    time.sleep(3)
                
                case 15:
                    js = Discord.getReportingGuildMenu(random.choice(self.tokens))
                    nodes = js["nodes"]
                    
                    breadcrumbs = [0]
                    idd = "0"
                    while True:
                        self.cns.clear()
                        self.cns.logo()
                    
                        current_node = nodes[idd]
                        if current_node["children"] == []:
                            break
                        
                        idd = self.cns.reportMenu(current_node["children"])
                            
                        breadcrumbs.append(int(idd))
                    
                    
                    self.cns.clear()
                    self.cns.logo()
                    
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    g = self.cns.input("Guild ID")
                    am = int(self.cns.input("Amount of reports"))
                    
                    tokens = self.split_list(self.tokens, int(threads))
                    
                    data = {
                        "variant": js["variant"],
                        "version": js["version"],
                        "language": "en"
                    }
                    
                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.report, args=(breadcrumbs, g, data, am, x,))
                        threads.append(a)
                        a.start()
                        
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                
                case 16:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    with open("data/avatar.png", "rb") as f:
                        avatar = f.read()
                    
                    tokens = self.split_list(self.tokens, int(threads))
                    
                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.avatar, args=(avatar, x,))
                        threads.append(a)
                        a.start()
                    
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                
                case 17:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    g = self.cns.input("Guild ID")
                    c = self.cns.input("Channel ID")
                    
                    soun_effects = ["quack", "airhorn", "cricket", "golf clap", "sad horn", "ba dum tss"]
                    emojis = {
                        "quack": "🦆",
                        "airhorn": "📣",
                        "cricket": "🦗",
                        "golf clap": "👏",
                        "sad horn": "🎺",
                        "ba dum tss": "🥁"
                    }
                    
                    s = self.cns.input(f"Sound effect ({', '.join(soun_effects)})")
                    
                    eff = soun_effects.index(s)+1
                    if s == "sad horn":
                        eff_rep = "sad_trombone"
                    else:
                        eff_rep = s.replace(" ", "_")
                    
                    data = {
                        "sound_id": eff,
                        "emoji_id": None,
                        "emoji_name": emojis[s],
                        "override_path": f"default_{eff_rep}.mp3",
                    }

                    tokens = self.split_list(self.tokens, int(threads))
                    
                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.soundboard, args=(c, g, data, x,))
                        threads.append(a)
                        a.start()
                    
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                
                case 18:
                    threads = self.cns.input(f"Threads (1-{len(self.tokens)})")
                    n = self.cns.input("Name")
                    
                    tokens = self.split_list(self.tokens, int(threads))
                    
                    threads = []
                    for x in tokens:
                        a = threading.Thread(target=self.displayName, args=(n, x,))
                        threads.append(a)
                        a.start()
                    
                    while threads != []:
                        for x in threads:
                            if not x.is_alive():
                                x.join()
                                threads.remove(x)
                    
                    time.sleep(3)
                    
                        
                        

if __name__ == "__main__":
    MTool2().start()
