🚀 Simulate realistic human traffic to Zillow and other real estate sites using the Tor network.  
☠️ Designed with a hacker-style aesthetic, HTML logging, rotating user agents, and stealthy headless browser fallbacks for challenge-bypassing.

---

## 🔧 Features

- ✅ Sends randomized visits via Tor to Zillow, Realtor.com, Remax, and Redfin
- 🔁 Changes identity with Tor (`NEWNYM`) every cycle
- 🧠 Auto-handles Zillow CAPTCHA/403/202 challenges via Chromium headless browser
- 💻 Generates beautiful HTML reports with full logs
- 🎨 Styled, colorized, and dramatic terminal output (like a real cyber console)
- 👥 Randomized User-Agent with each request
- 🔥 Smart request pacing with adaptive delays to simulate human browsing
- 💂 Built-in `sudo` escalation only when changing Tor identities

---

## 📸 Screenshot

```___                          _           _     _     _   _             
| ___ \                        | |         | |   (_)   | | (_)            
| |_/ / __ ___  _ __   ___ _ __| |_ _   _  | |    _ ___| |_ _ _ __   __ _ 
|  __/ '__/ _ \| '_ \ / _ \ '__| __| | | | | |   | / __| __| | '_ \ / _` |
| |  | | | (_) | |_) |  __/ |  | |_| |_| | | |___| \__ \ |_| | | | | (_| |
\_|  |_|  \___/| .__/ \___|_|   \__|\__, | \_____/_|___/\__|_|_| |_|\__, |
               | |                   __/ |                           __/ |
               |_|                  |___/                           |___/ 
______                 _                                                  
| ___ \               | |                                                 
| |_/ / ___   ___  ___| |_ ___ _ __                                       
| ___ \/ _ \ / _ \/ __| __/ _ \ '__|                                      
| |_/ / (_) | (_) \__ \ ||  __/ |                                         
\____/ \___/ \___/|___/\__\___|_|                                         
─── Property Listing Booster -ICNET - TOR ───
```

---

## 🖥️ Requirements

### 🔗 System Dependencies

Before running the script, make sure the following are installed on **Ubuntu or Debian-based systems**:

```bash
sudo apt update && sudo apt install -y   tor   python3   python3-pip   libglib2.0-0   libnss3   libgconf-2-4   libxss1   libappindicator1   libindicator7   fonts-liberation   xdg-utils   snapd
```

Install Chromium via Snap (required for headless bypass):

```bash
sudo snap install chromium
```

Enable and start Tor daemon:

```bash
sudo systemctl enable tor
sudo systemctl start tor
```
⚠️ Important Note for Users:

If you're not using a virtual environment, you may need to use the --break-system-packages flag when installing the dependencies:

pip install -r requirements.txt --break-system-packages

This avoids issues with Python's system environment on some Linux distributions. 

Or manually:

```bash
pip3 install requests stem fake-useragent colorama beautifulsoup4 undetected-chromedriver --break-system-packages
```

---

## 📁 Project Structure

```
tor-traffic-booster/
├── Property-Listing-Booster.py              ← Main script
├── traffic_report.html     ← Output logs (generated)
├── requirements.txt        ← Python dependencies
└── README.md               ← You are here
```

---

## 🧪 Usage

1. Run the script with Python 3:
   ```bash
   python3 booster.py
   ```

2. Enter real estate listing URLs when prompted:
   ```
   Enter Zillow listing URL: https://www.zillow.com/homedetails/123-Example-St/000000_zpid/
   Enter Realtor.com URL: 
   Enter Remax.com URL: 
   Enter Redfin.com URL: 
   ```

3. Logs will be printed to terminal and exported as `traffic_report.html`.

> 💡 Headless browser launches if Zillow returns HTTP 202 or 403 to simulate real traffic from a virtual user.

---

## 🔒 Notes

- The script uses `sudo` **only** when changing Tor identity. This minimizes security risks.
- Your real IP may appear briefly when first querying; only site visits route through Tor.
- Zillow's anti-bot behavior is monitored — if 403 or 202 is detected, stealth browser emulation activates.
- Headless browser uses `/snap/bin/chromium` (default Snap path).

---

## 🧙 Tips for Best Results

- Start with one URL to validate Tor routing works.
- Leave long intervals (default: ~60–90 seconds) between hits.
- Run for hours/days for consistent traffic build-up.
- Use `tmux` or `screen` to keep sessions alive when running on remote systems.

---

## 🧠 Disclaimer

This tool is provided for **educational and research purposes** only.  
**Do not** use it to artificially inflate traffic or violate terms of service on third-party platforms.

---

## 🧰 Credits

Developed with ❤️ by **InterCuba.Net**  
---
