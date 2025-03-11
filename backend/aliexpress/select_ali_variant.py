import pyautogui
import pyperclip
import time
import pytoolsx as pt
from PIL import ImageOps
from pytesseract import image_to_data, Output

def select_variant(ali_value):
  os = "windows"  # Set to 'mac' or 'windows'
  js = f'var e = document.querySelector(\'img[alt="{ali_value}"]\'); e ? e.click() : console.error("Not found");'
  pyperclip.copy(js)
  hotkey = ('command', 'option', 'j') if os == 'mac' else ('ctrl', 'shift', 'j')
  pyautogui.hotkey(*hotkey); time.sleep(1.5)
  pyautogui.hotkey('command' if os == 'mac' else 'ctrl', 'v'); pyautogui.press('enter')
  pyautogui.hotkey(*hotkey)  # Close DevTools
  time.sleep(1)

  def ocr(region, invert=False, debug=False):
    """Performs OCR on a region, returns text as a string."""
    screenshot = pyautogui.screenshot().convert("RGB")
    if region:
        x1, y1, x2, y2 = region
        screenshot = screenshot.crop((x1, y1, x2, y2))
    if invert:
        screenshot = ImageOps.invert(screenshot)
    data = image_to_data(screenshot, output_type=Output.DICT)
    extracted_text = " ".join(data['text'][i].strip() for i in range(len(data['text'])) if data['text'][i].strip())
    if debug:
        print(f"OCR Result: {extracted_text}")
    return extracted_text
  
  # Find "Color:" label on the page
  ali_ref = pt.findOnPage(["Color:", "Name:"], loop=True)
  vnamex, vnamey = ali_ref
  vname_area = (vnamex - 50, vnamey - 25, vnamex + 300, vnamey + 25)
  if ali_value in ocr(vname_area, debug=True):
     return True
  else:
     False