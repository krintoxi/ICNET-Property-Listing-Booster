#!/usr/bin/env python3
import sys
import time
from stem import Signal
from stem.control import Controller

TOR_CONTROL_PORT = 9051

def change_identity():
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate()  # expects cookie or no password
            controller.signal(Signal.NEWNYM)
            time.sleep(5)
        print("SUCCESS")
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    change_identity()
