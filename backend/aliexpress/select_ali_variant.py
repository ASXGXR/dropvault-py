import pyautogui
import pyperclip
import time
import pytoolsx as pt

def select_variant(ali_value, size=""):
  os = "windows"  # Set to 'mac' or 'windows'
  js = f'var e = document.querySelector(\'img[alt="{ali_value}"]\'); e ? e.click() : console.error("Not found");'
  pyperclip.copy(js)
  hotkey = ('command', 'option', 'j') if os == 'mac' else ('ctrl', 'shift', 'j')
  pyautogui.hotkey(*hotkey); time.sleep(1.5)
  if "what" in pt.ocr((2058, 1207, 2558, 1439)).lower():
     pyautogui.click(2538, 1234)
     time.sleep(1)
     pyautogui.click(2362, 1400)
     time.sleep(0.5)
  pyautogui.hotkey('command' if os == 'mac' else 'ctrl', 'v'); pyautogui.press('enter')

  if size:
    js_size = f'var e = Array.from(document.querySelectorAll("div[title]")).find(el => el.title.includes("{size}")); e ? e.click() : console.error("Size not found");'
    pyperclip.copy(js_size)
    pyautogui.hotkey('command' if os == 'mac' else 'ctrl', 'v'); pyautogui.press('enter')

  pyautogui.hotkey(*hotkey)  # Close DevTools
  time.sleep(1)
  
  # Find "Color:" label on the page
  ali_ref = pt.findOnPage(["Color:", "Name:"], loop=True)
  vnamex, vnamey = ali_ref
  vname_area = (vnamex - 50, vnamey - 25, vnamex + 300, vnamey + 25)
  if ali_value in pt.ocr(vname_area):
     return True
  else:
     print(f"Ali value: {ali_value} not found on page. Wrong variant selected?")
     return False