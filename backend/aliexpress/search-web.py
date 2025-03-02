import sys
import platform
import subprocess
import time
import pyautogui
import pyperclip
import urllib.parse
import pygetwindow as gw

if len(sys.argv) < 2:
    sys.exit("Usage: python search_web.py <product_title>")

title = sys.argv[1]
search_url = "https://www.google.com/search?q=" + urllib.parse.quote(title)

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
        else:
            subprocess.run("start chrome", shell=True)
    except ImportError:
        subprocess.run("start chrome", shell=True)
    ctrl_key = "ctrl"
else:
    ctrl_key = "ctrl"

time.sleep(1)
print(f"Searching Google for: {title}")

# Open a new tab in Chrome and paste the search URL
pyautogui.hotkey(ctrl_key, "t")
time.sleep(0.5)
pyperclip.copy(search_url)
pyautogui.hotkey(ctrl_key, "v")
pyautogui.press("enter")