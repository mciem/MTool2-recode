from base64     import b64encode             
from json       import dumps
from pypresence import Presence
from time       import time, sleep

def XSuperProperties(buildNum: int):
    return b64encode(dumps({"os":"Windows","browser":"Chrome","device":"","system_locale":"pl-PL","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36","browser_version":"110.0.0.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":buildNum,"client_event_source":None,"design_id":0}).encode()).decode()

def handleRatelimit(js):
    retry_after = js["retry_after"]
    sleep(retry_after)

def presence():
    client_id = "1100445415624675328"
    RPC = Presence(client_id=client_id)
    RPC.connect()

    RPC.update(state="Raiding servers using MTool2", start=time()*1000, buttons=[{"label": "Discord", "url": "https://discord.gg/HspytEMhfR"}, {"label": "YouTube", "url": "https://www.youtube.com/watch?v=-qfLTw3WOIc"}], large_image="github-mark")
