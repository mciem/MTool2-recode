from tls_client import Session
from colorama import Fore


class Client:
    def __init__(self) -> None:
        self.headers = {
			"accept":             "*/*",
			"accept-language":    "en-US;q=0.8,en;q=0.7",
			"content-type":       "application/json",
			"host":               "discord.com",
			"origin":             "https://discord.com",
			"sec-ch-ua":          '"Chromium";v="110", "Google Chrome";v="110", "Not;A=Brand";v="99"',
			"sec-ch-ua-mobile":   "?0",
			"sec-ch-ua-platform": '"Windows"',
			"sec-fetch-dest":     "empty",
			"sec-fetch-mode":     "cors",
			"sec-fetch-site":     "same-origin",
			"user-agent":         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        }
        
        ja3 = "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,10-0-43-5-23-13-65281-45-17513-35-51-18-27-11-16-21,29-23-24,0"
        self.session = Session(ja3_string=ja3,h2_settings={
			"HEADER_TABLE_SIZE": 65536,
			"MAX_CONCURRENT_STREAMS": 1000,
			"INITIAL_WINDOW_SIZE": 6291456,
			"MAX_HEADER_LIST_SIZE": 262144
		},
		h2_settings_order=[
			"HEADER_TABLE_SIZE",
			"MAX_CONCURRENT_STREAMS",
			"INITIAL_WINDOW_SIZE",
			"MAX_HEADER_LIST_SIZE"
		],
		supported_signature_algorithms=[
			"ECDSAWithP256AndSHA256",
			"PSSWithSHA256",
			"PKCS1WithSHA256",
			"ECDSAWithP384AndSHA384",
			"PSSWithSHA384",
			"PKCS1WithSHA384",
			"PSSWithSHA512",
			"PKCS1WithSHA512",
		],
		supported_versions=["GREASE", "1.3", "1.2"],
		key_share_curves=["GREASE", "X25519"],
		cert_compression_algo="brotli",
		pseudo_header_order=[
			":method",
			":authority",
			":scheme",
			":path"
		],
		connection_flow=15663105)
	
        self.session.get("https://discord.com", headers=self.headers)
        
        self.headers["cookie"] = "; ".join(f"{k}={v}" for k,v in self.session.cookies.items())
        self.headers["x-discord-locale"] = "pl"
        self.headers["x-discord-timezone"] = "Europe/Warsaw"
        self.headers["x-debug-options"] = "bugReporterEnabled"