import sys
import platform
import subprocess
import time
import pyautogui
import pyperclip
import urllib.parse
import pygetwindow as gw

if len(sys.argv) < 2:
    sys.exit("Usage: python search_web.py <url>")

search_url = sys.argv[1]

launched = False

# Activate Google Chrome based on the OS
if platform.system() == 'Darwin':
    subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'])
    ctrl_key = "command"
elif platform.system() == 'Windows':
    try:
        chrome_windows = gw.getWindowsWithTitle('Chrome')
        if chrome_windows:
            try:
                chrome_windows[0].activate()
            except Exception as e:
                print(f"Error activating Chrome window: {e}. Launching new Chrome instance.")
                subprocess.run("start chrome", shell=True)
                launched = True
        else:
            subprocess.run("start chrome", shell=True)
            launched = True
    except ImportError:
        subprocess.run("start chrome", shell=True)
        launched = True
    ctrl_key = "ctrl"
else:
    ctrl_key = "ctrl"

time.sleep(1)

# Only open a new tab if Chrome was already running
if not launched:
    pyautogui.hotkey(ctrl_key, "t")
    time.sleep(0.5)
else:
    # If Chrome was just launched, wait a bit more for it to settle
    time.sleep(1)

pyperclip.copy(search_url)
pyautogui.hotkey(ctrl_key, "v")
pyautogui.press("enter")

time.sleep(4) # wait for page to load