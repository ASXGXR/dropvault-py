import pyautogui
import pyperclip
import time
import pytoolsx as pt

wait_time = 1.5
ON_LAPTOP = True
if ON_LAPTOP: # Laptop co-ords
    CONSOLE_AREA = (1224, 581, 1919, 1079)
    CONSOLE_CLICK = (1858, 980)
else: # Desktop co-ords
    CONSOLE_AREA = (1633, 775, 2559, 1439)
    CONSOLE_CLICK = (2478, 1356)

def select_variant(ali_value, size=""):
  
  os = "windows"  # Set to 'mac' or 'windows'
  js = f'var e = document.querySelector(\'img[alt="{ali_value}"]\'); e ? e.click() : console.error("Not found");'
  pyperclip.copy(js)
  hotkey = ('command', 'option', 'j') if os == 'mac' else ('ctrl', 'shift', 'j')
  pyautogui.hotkey(*hotkey)
  time.sleep(wait_time*1.5)
  pt.clickFindOnPage("Console",area=CONSOLE_AREA, timeout=5)
  time.sleep(wait_time/2)
  pyautogui.click(CONSOLE_CLICK)
  time.sleep(wait_time/3)
  pyautogui.hotkey('command' if os == 'mac' else 'ctrl', 'v'); pyautogui.press('enter')

  if size:
    js_size = f'var e = Array.from(document.querySelectorAll("div[title]")).find(el => el.title.includes("{size}")); e ? e.click() : console.error("Size not found");'
    pyperclip.copy(js_size)
    pyautogui.hotkey('command' if os == 'mac' else 'ctrl', 'v'); pyautogui.press('enter')

  pyautogui.hotkey(*hotkey)  # Close DevTools
  time.sleep(1)
  
  # Check if ali value found on page
  ali_ref = pt.findOnPage(["Color:", "Name:"], loop=True)
  vnamex, vnamey = ali_ref
  vname_area = (vnamex - 50, vnamey - 25, vnamex + 300, vnamey + 25)
  if ali_value in pt.ocr(vname_area): return True
  else: return False