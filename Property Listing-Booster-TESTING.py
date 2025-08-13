import os
import time
import random
import subprocess
import threading
import requests
import pyautogui
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
from colorama import init, Fore, Style

init(autoreset=True)

# === GLOBAL SETTINGS ===
CHROMIUM_PATH = "/usr/bin/google-chrome"  # Change if needed
VISITS_PER_DAY = 200
HEADLESS_WAIT_RANGE = (9, 14)
WAIT_BETWEEN_VISITS = (10, 20)
HTML_REPORT = "traffic_report-icn.html"

LOG_LINES = []
stop_flag = threading.Event()

# === LOGGING ===
def log(msg, level="INFO", gui=None):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    color = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED
    }.get(level.upper(), Fore.CYAN)
    formatted_console = f"{Fore.YELLOW + Style.BRIGHT}{timestamp} {color}{msg}"
    formatted_plain = f"{timestamp} {level.upper()}: {msg}"
    LOG_LINES.append(formatted_plain)
    print(formatted_console)
    if gui:
        gui.after(0, lambda: gui.log_text.insert(tk.END, formatted_plain + "\n"))
        gui.after(0, lambda: gui.log_text.see(tk.END))

# === TOR IDENTITY ===
def request_new_tor_identity(gui=None):
    if gui and not gui.use_tor.get():
        log("Tor identity request skipped because Tor is OFF.", level="WARNING", gui=gui)
        return
    log("Requesting New Tor Identity...", level="INFO", gui=gui)
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
        log("New Tor identity requested successfully.", level="SUCCESS", gui=gui)
    except Exception:
        try:
            log("Trying with sudo to change identity...", level="WARNING", gui=gui)
            subprocess.run(["sudo", "killall", "-HUP", "tor"], check=True)
            log("Successfully changed Tor identity using sudo.", level="SUCCESS", gui=gui)
        except Exception as ex:
            log(f"Failed to change Tor identity: {ex}", level="ERROR", gui=gui)

# === USER-AGENT ===
def get_random_headers():
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.9',
    }

# === PUBLIC IP ===
def get_current_ip(gui=None):
    try:
        session = requests.Session()
        if gui and gui.use_tor.get():
            session.proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
        ip = session.get("https://api.ipify.org", timeout=10).text
        return ip
    except:
        return "Unknown"

# --- simulate human-like mouse movements ---
def simulate_mouse_interaction(gui=None):
    try:
        log("Simulating human-like mouse interaction...", level="INFO", gui=gui)
        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        for _ in range(5):
            if stop_flag.is_set():
                return
            offset_x = random.randint(-100, 100)
            offset_y = random.randint(-100, 100)
            pyautogui.moveTo(center_x + offset_x, center_y + offset_y, duration=1)
            time.sleep(0.7)
        pyautogui.scroll(-200)
        time.sleep(1.5)
        pyautogui.scroll(100)
        time.sleep(1.5)
        click_x = center_x + random.randint(-50, 50)
        click_y = center_y + random.randint(-50, 50)
        pyautogui.click(click_x, click_y)
        log(f"Clicked at ({click_x}, {click_y})", level="INFO", gui=gui)
        time.sleep(3)
    except Exception as e:
        log(f"Mouse interaction simulation failed: {e}", level="ERROR", gui=gui)

# === CAPTCHA solver with pyautogui ===
def handle_captcha_with_pyautogui(driver, gui=None):
    try:
        log("Attempting to simulate human click-and-hold with pyautogui...", level="INFO", gui=gui)
        time.sleep(2)
        driver.maximize_window()
        driver.set_window_position(0, 0)
        time.sleep(2)
        screen_width, screen_height = pyautogui.size()
        click_x = screen_width // 2
        click_y = screen_height // 2 + 100
        log(f"Moving to CAPTCHA button at ({click_x}, {click_y})...", level="INFO", gui=gui)
        pyautogui.moveTo(click_x, click_y, duration=1)
        pyautogui.mouseDown()
        log("Holding mouse down for 8 seconds...", level="INFO", gui=gui)
        time.sleep(8.5)
        pyautogui.mouseUp()
        log("Released mouse — CAPTCHA simulation complete.", level="SUCCESS", gui=gui)
        time.sleep(3)
        simulate_mouse_interaction(gui=gui)
    except Exception as e:
        log(f"PyAutoGUI CAPTCHA simulation failed: {e}", level="ERROR", gui=gui)

# === Launch undetected Chrome routed through Tor if enabled ===
def launch_headless_browser(url, gui=None):
    print(Fore.BLUE + "\n### Launching Headless Browser Session ###")
    driver = None
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        options = uc.ChromeOptions()
        options.headless = False  # Must be False for pyautogui to work
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.binary_location = CHROMIUM_PATH

        if gui and gui.use_tor.get():
            options.add_argument("--proxy-server=socks5://127.0.0.1:9050")
            log("Launching browser with Tor proxy enabled.", gui=gui)
        else:
            log("Launching browser WITHOUT Tor proxy.", gui=gui)

        driver = uc.Chrome(options=options)
        driver.set_window_size(1280, 1024)
        driver.set_window_position(0, 0)

        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        log("Page fully loaded, starting mouse interaction...", level="INFO", gui=gui)

        # Check browser IP via new tab
        driver.execute_script("window.open('https://api.ipify.org');")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)
        ip_text = driver.find_element(By.TAG_NAME, "body").text.strip()
        log(f"Browser public IP (via Tor proxy): {ip_text}", level="INFO", gui=gui)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        page_source = driver.page_source.lower()
        if any(phrase in page_source for phrase in [
            "verify you’re a human", "click and hold", "robot check", "unusual traffic"]):
            log("CAPTCHA detected in page source!", level="WARNING", gui=gui)
            handle_captcha_with_pyautogui(driver, gui=gui)
        else:
            log("No CAPTCHA detected.", level="SUCCESS", gui=gui)
            simulate_mouse_interaction(gui=gui)

        wait_time = round(random.uniform(*HEADLESS_WAIT_RANGE), 1)
        log(f"Waiting {wait_time} seconds to simulate human activity...", level="INFO", gui=gui)
        time.sleep(wait_time)

    except Exception as e:
        log(f"Headless browser error: {e}", level="ERROR", gui=gui)

    finally:
        if driver:
            log("Pausing 3 seconds before closing browser...", level="INFO", gui=gui)
            time.sleep(3)
            driver.quit()
            log("Browser session closed.", level="SUCCESS", gui=gui)
        time.sleep(2)

# === Visit function now uses browser for ALL platforms ===
def visit_url(platform, url, gui=None):
    headers = get_random_headers()
    log(f"Visiting {platform}: {url} with User-Agent: {headers['User-Agent']}", level="INFO", gui=gui)
    try:
        launch_headless_browser(url, gui=gui)
        log(f"Completed browser visit for {platform}.", gui=gui)
    except Exception as e:
        log(f"Error visiting {platform}: {e}", level="ERROR", gui=gui)

# === Export HTML report ===
def export_report(gui=None):
    log("Exporting HTML Report...", level="INFO", gui=gui)
    try:
        with open(HTML_REPORT, "w") as f:
            f.write("<html><head><title>Tor Traffic Booster Log</title><style>")
            f.write("body{background:#000;color:#0f0;font-family:monospace;padding:10px;}")
            f.write("</style></head><body><h2>Tor Traffic Booster - Report</h2><pre>")
            for line in LOG_LINES:
                f.write(line + "\n")
            f.write(f"</pre><p><b>Last Known IP:</b> {get_current_ip(gui=gui)}</p></body></html>")
        log(f"HTML report exported to {HTML_REPORT}.", level="SUCCESS", gui=gui)
    except Exception as e:
        log(f"Failed to export HTML report: {e}", level="ERROR", gui=gui)

# === Background thread main loop ===
def booster_loop(urls, gui):
    log(f"Starting simulation: ~{VISITS_PER_DAY} visits per platform per day.", gui=gui)
    while not stop_flag.is_set():
        for name, url in urls:
            if stop_flag.is_set():
                log("Stopping booster loop as requested.", level="INFO", gui=gui)
                return

            ip_before = get_current_ip(gui=gui)
            log(f"Current IP before identity change: {ip_before}", gui=gui)

            request_new_tor_identity(gui=gui)
            time.sleep(5)

            ip_after = get_current_ip(gui=gui)
            log(f"Current IP after identity change: {ip_after}", gui=gui)

            if ip_before == ip_after:
                log("[WARNING] IP did NOT change after Tor identity request!", level="WARNING", gui=gui)
            else:
                log("IP changed successfully after Tor identity request.", level="SUCCESS", gui=gui)

            visit_url(name, url, gui=gui)

            sleep_time = round(random.uniform(*WAIT_BETWEEN_VISITS), 1)
            log(f"Waiting {sleep_time} seconds before next request...", gui=gui)
            for _ in range(int(sleep_time)):
                if stop_flag.is_set():
                    break
                time.sleep(1)
            else:
                time.sleep(sleep_time - int(sleep_time))

        export_report(gui=gui)

# === GUI APP ===
class BoosterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Property Listing Traffic Booster")
        self.geometry("900x650")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.use_tor = tk.BooleanVar(value=True)

        # Input URLs frame
        input_frame = ttk.LabelFrame(self, text="Input URLs")
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.entries = {}
        for platform in ["Zillow", "Realtor", "Remax", "Redfin"]:
            lbl = ttk.Label(input_frame, text=f"{platform} URL:")
            lbl.pack(anchor=tk.W, padx=5, pady=2)
            ent = ttk.Entry(input_frame, width=100)
            ent.pack(fill=tk.X, padx=5, pady=2)
            self.entries[platform] = ent

        # Tor On/Off switch
        tor_frame = ttk.LabelFrame(self, text="Tor Proxy Control")
        tor_frame.pack(fill=tk.X, padx=10, pady=5)

        tor_switch = ttk.Checkbutton(tor_frame, text="Use Tor Network (On/Off)", variable=self.use_tor)
        tor_switch.pack(anchor=tk.W, padx=5, pady=5)

        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_booster)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_booster, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = ttk.Button(btn_frame, text="Export Report", command=self.export_report)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Log output
        log_frame = ttk.LabelFrame(self, text="Log Output")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, bg="black", fg="lime", font=("Courier", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.worker_thread = None

    def start_booster(self):
        urls = [(p, e.get().strip()) for p, e in self.entries.items() if e.get().strip()]
        if not urls:
            messagebox.showwarning("Input Error", "Please enter at least one URL to start.")
            return

        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("Already Running", "Booster is already running.")
            return

        stop_flag.clear()
        self.log_text.delete(1.0, tk.END)
        self.worker_thread = threading.Thread(target=booster_loop, args=(urls, self), daemon=True)
        self.worker_thread.start()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

    def stop_booster(self):
        if messagebox.askyesno("Stop Booster", "Are you sure you want to stop the booster?"):
            stop_flag.set()
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            log("Booster stopped by user.", gui=self)

    def export_report(self):
        export_report(gui=self)
        messagebox.showinfo("Export Report", f"Report exported to {HTML_REPORT}.")

    def on_close(self):
        if self.worker_thread and self.worker_thread.is_alive():
            if not messagebox.askyesno("Exit", "Booster is running. Stop it and exit?"):
                return
            stop_flag.set()
            self.worker_thread.join()
        self.destroy()

if __name__ == "__main__":
    app = BoosterGUI()
    app.mainloop()
