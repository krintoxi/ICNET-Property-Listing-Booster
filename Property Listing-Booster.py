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
import pyautogui

init(autoreset=True)

# === GLOBAL SETTINGS ===
ZILLOW_ONLY_HEADLESS = True
ZILLOW_EXPECTS_202 = True
CHROMIUM_PATH = "/snap/bin/chromium"
VISITS_PER_DAY = 200
HEADLESS_WAIT_RANGE = (9, 14)
WAIT_BETWEEN_VISITS = (10, 20)
HTML_REPORT = "traffic_report-icn.html"
LOG_LINES = []

# === ASCII HEADER ===
def show_banner():
    print(Fore.GREEN + Style.BRIGHT)
    print("""
______                          _           _     _     _   _                
| ___ \                        | |         | |   (_)   | | (_)               
| |_/ / __ ___  _ __   ___ _ __| |_ _   _  | |    _ ___| |_ _ _ __   __ _    
|  __/ '__/ _ \| '_ \ / _ \ '__| __| | | | | |   | / __| __| | '_ \ / _` |   
| |  | | | (_) | |_) |  __/ |  | |_| |_| | | |___| \__ \ |_| | | | | (_| |   
\_|  |_|  \___/| .__/ \___|_|   \__|\__, | \_____/_|___/\__|_|_| |_|\__, |   
               | |                   __/ |                           __/ |   
______         |_|     _            |___/_   ______ _____ _____ ___ |___/    
| ___ \               | |             /\| |/\| ___ \  ___|_   _/ _ \ /\| |/\ 
| |_/ / ___   ___  ___| |_ ___ _ __   \ ` ' /| |_/ / |__   | |/ /_\ \\ ` ' / 
| ___ \/ _ \ / _ \/ __| __/ _ \ '__| |_     _| ___ \  __|  | ||  _  |_     _|
| |_/ / (_) | (_) \__ \ ||  __/ |     / , . \| |_/ / |___  | || | | |/ , . \ 
\____/ \___/ \___/|___/\__\___|_|     \/|_|\/\____/\____/  \_/\_| |_/\/|_|\/                                                                                                                                                                                                    
""")
    print(Fore.RED + Style.BRIGHT + "───  [🏠] Property Listing Booster — Powered by Python3 & Tor 🐍")

# === LOGGING ===
def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    color = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED
    }.get(level.upper(), Fore.CYAN)
    formatted = f"{Fore.YELLOW + Style.BRIGHT}{timestamp} {color}{msg}"
    LOG_LINES.append(f"{timestamp} {msg}")
    print(formatted)

# === TOR IDENTITY ===
def request_new_tor_identity():
    print(Fore.MAGENTA + "\n### Requesting New Tor Identity ###")
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
        log("New Tor identity requested successfully.", level="SUCCESS")
    except Exception:
        try:
            log("Trying with sudo to change identity...", level="WARNING")
            subprocess.run(["sudo", "killall", "-HUP", "tor"], check=True)
            log("Successfully changed Tor identity using sudo.", level="SUCCESS")
        except Exception as ex:
            log(f"Failed to change Tor identity: {ex}", level="ERROR")

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

# --- helper: simulate human browsing mouse interaction ---
def simulate_mouse_interaction():
    try:
        log("Simulating human-like mouse interaction...", level="INFO")
        screen_width, screen_height = pyautogui.size()

        # Move mouse in a small random pattern near center, slower moves and pauses
        center_x = screen_width // 2
        center_y = screen_height // 2
        for _ in range(5):
            offset_x = random.randint(-100, 100)
            offset_y = random.randint(-100, 100)
            pyautogui.moveTo(center_x + offset_x, center_y + offset_y, duration=1)  # slower move
            time.sleep(0.7)  # longer pause

        # Scroll down a bit slowly, then up slowly
        pyautogui.scroll(-200)
        time.sleep(1.5)
        pyautogui.scroll(100)
        time.sleep(1.5)

        # Random click near center to simulate interaction
        click_x = center_x + random.randint(-50, 50)
        click_y = center_y + random.randint(-50, 50)
        pyautogui.click(click_x, click_y)
        log(f"Clicked at ({click_x}, {click_y})", level="INFO")
        time.sleep(3)  # longer pause after click

    except Exception as e:
        log(f"Mouse interaction simulation failed: {e}", level="ERROR")

# === CAPTCHA SOLVER ===
def handle_captcha_with_pyautogui(driver):
    try:
        log("Attempting to simulate human click-and-hold with pyautogui...", level="INFO")
        time.sleep(2)
        driver.maximize_window()
        driver.set_window_position(0, 0)
        time.sleep(2)

        screen_width, screen_height = pyautogui.size()
        click_x = screen_width // 2
        click_y = screen_height // 2 + 100  # Adjust as needed

        log(f"Moving to CAPTCHA button at ({click_x}, {click_y})...", level="INFO")
        pyautogui.moveTo(click_x, click_y, duration=1)
        pyautogui.mouseDown()
        log("Holding mouse down for 8 seconds...", level="INFO")
        time.sleep(8.5)
        pyautogui.mouseUp()
        log("Released mouse — CAPTCHA simulation complete.", level="SUCCESS")
        time.sleep(3)

        # After CAPTCHA solved, do some browsing interaction
        simulate_mouse_interaction()

    except Exception as e:
        log(f"PyAutoGUI CAPTCHA simulation failed: {e}", level="ERROR")

# === HEADLESS BROWSER ===
def launch_headless_browser(url):
    print(Fore.BLUE + "\n### Launching Headless Browser Session ###")
    driver = None
    try:
        from selenium import webdriver
        import undetected_chromedriver as uc
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        options = uc.ChromeOptions()
        options.headless = False  # Must be False for pyautogui to work
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.binary_location = CHROMIUM_PATH

        log(f"Using Chrome/Chromium binary at {CHROMIUM_PATH}", level="INFO")
        driver = uc.Chrome(options=options)
        driver.set_window_size(1280, 1024)
        driver.set_window_position(0, 0)

        driver.get(url)

        # Wait for main content or body element to be loaded (up to 15 seconds)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        log("Page fully loaded, starting mouse interaction...", level="INFO")

        page_source = driver.page_source.lower()
        if any(phrase in page_source for phrase in [
            "verify you’re a human", "click and hold", "robot check", "unusual traffic"]):
            log("Zillow CAPTCHA detected in page source!", level="WARNING")
            handle_captcha_with_pyautogui(driver)
        else:
            log("No CAPTCHA detected.", level="SUCCESS")
            # Simulate mouse interaction even if no captcha
            simulate_mouse_interaction()

        wait_time = round(random.uniform(*HEADLESS_WAIT_RANGE), 1)
        log(f"Headless browser waiting {wait_time} seconds to simulate human activity...", level="INFO")
        time.sleep(wait_time)

    except Exception as e:
        log(f"Headless browser error: {e}", level="ERROR")

    finally:
        if driver:
            # Add an extra 3 seconds so interaction can be visually confirmed before closing
            log("Pausing 3 seconds before closing browser...", level="INFO")
            time.sleep(3)
            driver.quit()
            log("Headless browser session closed.", level="SUCCESS")
        time.sleep(2)  # brief pause before next launch to ensure clean closure

# === VISIT FUNCTION ===
def visit_url(platform, url):
    headers = get_random_headers()
    log(f"Visiting {platform}: {url} with User-Agent: {headers['User-Agent']}", level="INFO")
    try:
        if platform.lower() == "zillow":
            launch_headless_browser(url)
            log(f"Completed headless browser visit for Zillow.", level="SUCCESS")
        else:
            session = requests.Session()
            session.proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
            response = session.get(url, headers=headers, timeout=15)
            log(f"Response {response.status_code} — {platform} visit recorded.", level="INFO")
    except Exception as e:
        log(f"Error visiting {platform}: {e}", level="ERROR")

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
            f.write(f"</pre><p><b>Last Known IP:</b> {get_current_ip()}</p></body></html>")
        log(f"HTML report exported to {HTML_REPORT}.", level="SUCCESS")
    except Exception as e:
        log(f"Failed to export HTML report: {e}", level="ERROR")

# === MAIN LOOP ===
def main():
    show_banner()
    zillow = input("Enter Zillow listing URL (or leave blank): ")
    realtor = input("Enter Realtor.com URL (or leave blank): ")
    remax = input("Enter Remax.com URL (or leave blank): ")
    redfin = input("Enter Redfin.com URL (or leave blank): ")

    targets = [("Zillow", zillow), ("Realtor", realtor), ("Remax", remax), ("Redfin", redfin)]
    targets = [(name, url) for name, url in targets if url.strip() != ""]

    log(f"Starting simulation: ~{VISITS_PER_DAY} visits per platform per day.", level="INFO")

    while True:
        for name, url in targets:
            ip_before = get_current_ip()
            log(f"Current IP before identity change: {ip_before}", level="INFO")

            request_new_tor_identity()
            time.sleep(5)

            ip_after = get_current_ip()
            log(f"Current IP after identity change: {ip_after}", level="INFO")

            if ip_before == ip_after:
                log("[WARNING] IP did NOT change after Tor identity request!", level="WARNING")
            else:
                log("IP changed successfully after Tor identity request.", level="SUCCESS")

            visit_url(name, url)
            sleep_time = round(random.uniform(*WAIT_BETWEEN_VISITS), 1)
            log(f"Waiting {sleep_time} seconds before next request...", level="INFO")
            time.sleep(sleep_time)

        export_report()

if __name__ == '__main__':
    main()
