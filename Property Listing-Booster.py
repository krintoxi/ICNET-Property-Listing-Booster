# Property Listing BOOSTER v1 by ICNET
# Simulates anonymous traffic using rotating Tor identities and headless browser CAPTCHA bypass

import os
import sys
import time
import random
import subprocess
import shutil
import requests
import threading
from datetime import datetime
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from colorama import init, Fore, Style

init(autoreset=True)

# === GLOBAL SETTINGS ===
ZILLOW_ONLY_HEADLESS = True
ZILLOW_EXPECTS_202 = True
CHROMIUM_PATH = "/snap/bin/chromium"
VISITS_PER_DAY = 81
HEADLESS_WAIT_RANGE = (9, 14)
WAIT_BETWEEN_VISITS = (60, 90)
HTML_REPORT = "traffic_report.html"
LOG_LINES = []

# === ASCII HEADER ===
def show_banner():
    print(Fore.GREEN + Style.BRIGHT)
    print("""
```___                          _           _     _     _   _             
| ___ \                        | |         | |   (_)   | | (_)            
| |_/ / __ ___  _ __   ___ _ __| |_ _   _  | |    _ ___| |_ _ _ __   __ _ 
|  __/ '__/ _ \| '_ \ / _ \ '__| __| | | | | |   | / __| __| | '_ \ / _` |
| |  | | | (_) | |_) |  __/ |  | |_| |_| | | |___| \__ \ |_| | | | | (_| |
\_|  |_|  \___/| .__/ \___|_|   \__|\__, | \_____/_|___/\__|_|_| |_|\__, |
               | |                   __/ |                           __/ |
               |_|                  |___/                           |___/                                                  
| ___ \               | |                                                 
| |_/ / ___   ___  ___| |_ ___ _ __                                       
| ___ \/ _ \ / _ \/ __| __/ _ \ '__|                                      
| |_/ / (_) | (_) \__ \ ||  __/ |                                         
\____/ \___/ \___/|___/\__\___|_|                                         
─── Property Listing Booster -ICNET - TOR ───                                                         
""")
    print(Fore.RED + Style.BRIGHT + "───  [🏠] Property Listing Booster — Powered by Python3 & Tor 🐍")

# === LOGGING ===
def log(msg):
    timestamp = datetime.now().strftime(Fore.YELLOW + Style.BRIGHT + "[%Y-%m-%d %H:%M:%S]" + Style.RESET_ALL)
    formatted = f"{timestamp} {Fore.CYAN}{msg}"
    LOG_LINES.append(f"{timestamp} {msg}")
    print(formatted)

# === TOR IDENTITY ===
def request_new_tor_identity():
    print(Fore.MAGENTA + "\n### Requesting New Tor Identity ###")
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
        log("New Tor identity requested successfully.")
    except Exception:
        try:
            log("Trying with sudo to change identity...")
            subprocess.run(["sudo", "killall", "-HUP", "tor"], check=True)
            log("Successfully changed Tor identity using sudo.")
        except Exception as ex:
            log(f"Failed to change Tor identity: {ex}")

# === USER-AGENT ===
def get_random_headers():
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.9',
    }

# === PUBLIC IP ===
def get_current_ip():
    try:
        session = requests.Session()
        session.proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
        ip = session.get("https://api.ipify.org", timeout=10).text
        return ip
    except:
        return "Unknown"

# === HEADLESS BROWSER ===
def launch_headless_browser(url):
    print(Fore.BLUE + "\n### Launching Headless Browser Session ###")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import undetected_chromedriver as uc

        options = uc.ChromeOptions()
        options.headless = True
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.binary_location = CHROMIUM_PATH

        log(f"Using Chrome/Chromium binary at {CHROMIUM_PATH}")
        driver = uc.Chrome(options=options)
        driver.get(url)

        wait_time = round(random.uniform(*HEADLESS_WAIT_RANGE), 1)
        log(f"Headless browser waiting {wait_time} seconds to simulate human activity...")
        time.sleep(wait_time)
        driver.quit()
        log("Headless browser session completed.")
    except Exception as e:
        log(f"Headless browser error: {e}")

# === VISIT FUNCTION ===
def visit_url(platform, url):
    headers = get_random_headers()
    log(f"Visiting {platform}: {url} with User-Agent: {headers['User-Agent']}")
    try:
        if platform.lower() == "zillow":
            # Always use headless browser for Zillow to bypass protections
            launch_headless_browser(url)
            log(f"Completed headless browser visit for Zillow.")
        else:
            session = requests.Session()
            session.proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
            response = session.get(url, headers=headers, timeout=15)
            log(f"Response {response.status_code} — {platform} visit recorded.")
    except Exception as e:
        log(f"Error visiting {platform}: {e}")


# === HTML REPORT ===
def export_report():
    print(Fore.LIGHTYELLOW_EX + "\n### Exporting HTML Report ###")
    try:
        with open(HTML_REPORT, "w") as f:
            f.write("<html><head><title>Tor Traffic Booster Log</title><style>")
            f.write("body{background:#000;color:#0f0;font-family:monospace;padding:10px;}")
            f.write("</style></head><body><h2>Tor Traffic Booster - Report</h2><pre>")
            for line in LOG_LINES:
                f.write(line + "\n")
            f.write("</pre></body></html>")
        log(f"HTML report exported to {HTML_REPORT}.")
    except Exception as e:
        log(f"Failed to export HTML report: {e}")

# === MAIN LOOP ===
def main():
    show_banner()
    zillow = input("Enter Zillow listing URL (or leave blank): ")
    realtor = input("Enter Realtor.com URL (or leave blank): ")
    remax = input("Enter Remax.com URL (or leave blank): ")
    redfin = input("Enter Redfin.com URL (or leave blank): ")

    targets = [("Zillow", zillow), ("Realtor", realtor), ("Remax", remax), ("Redfin", redfin)]
    targets = [(name, url) for name, url in targets if url.strip() != ""]

    log(f"Starting simulation: ~{VISITS_PER_DAY} visits per platform per day.")

    while True:
        for name, url in targets:
            request_new_tor_identity()
            visit_url(name, url)
            sleep_time = round(random.uniform(*WAIT_BETWEEN_VISITS), 1)
            log(f"Waiting {sleep_time} seconds before next request...")
            time.sleep(sleep_time)
        export_report()

if __name__ == '__main__':
    main()
