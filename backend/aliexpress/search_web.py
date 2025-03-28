import platform
import subprocess
import time
import pyautogui
import pyperclip
import pygetwindow as gw

def searchWeb(url):
    os = platform.system()
    launched = False
    ctrl = "command" if os == "Darwin" else "ctrl"

    # --- macOS: activate and fullscreen Chrome ---
    if os == "Darwin":
        subprocess.run(["osascript", "-e", 'tell app "Google Chrome" to activate'])
        result = subprocess.run([
            "osascript", "-e",
            'tell app "System Events" to tell process "Google Chrome" '
            'to get value of attribute "AXFullScreen" of window 1'
        ], capture_output=True, text=True)

        if result.stdout.strip() != "true":
            subprocess.run(["osascript", "-e",
                'tell app "System Events" to keystroke "f" using {command down, control down}'])

    # --- Windows: activate or launch Chrome, maximise window ---
    elif os == "Windows":
        try:
            win = gw.getWindowsWithTitle("Chrome")
            if win:
                try:
                    win[0].activate()
                    try:
                        win[0].maximize()
                    except:
                        time.sleep(1)
                        pyautogui.hotkey('win', 'up')
                except:
                    subprocess.run("start chrome", shell=True)
                    launched = True
            else:
                subprocess.run("start chrome", shell=True)
                launched = True
        except:
            subprocess.run("start chrome", shell=True)
            launched = True

    # --- Open new tab if Chrome already running ---
    time.sleep(1 if launched else 0.5)
    if not launched:
        pyautogui.hotkey(ctrl, "t")
        time.sleep(0.3)

    # --- Paste URL and go ---
    pyperclip.copy(url)
    pyautogui.hotkey(ctrl, "v")
    pyautogui.press("enter")
    time.sleep(3) # Wait for page to load