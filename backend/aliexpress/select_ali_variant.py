import time
import pyautogui
from PIL import ImageOps
from pytesseract import image_to_data, Output
import pytoolsx as pt

def select_variant(variant_name):

  debug = True
  wait_time = 1.1  # Time between clicks
  d = 110  # Distance between variant boxes

  def ocr(region, invert=False):
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
        screenshot.save("test.png")
    return extracted_text
  
  def capture_variant(current_x, current_y, wait_time, vname_area, screenshot_index):
    """Clicks, waits, captures OCR text, and returns result."""
    pyautogui.click(current_x, current_y)
    if screenshot_index == 14:
        time.sleep(wait_time)
        pyautogui.click(current_x, current_y)
    time.sleep(wait_time)
    return ocr(vname_area)

  # Find "Color:" label on the page
  ali_ref = pt.findOnPage(["Color:", "Name:"], loop=True)
  v = [ali_ref[0] - 20, ali_ref[1] + 60]  # first variant position
  vnamex, vnamey = ali_ref
  vname_area = (vnamex - 50, vnamey - 25, vnamex + 300, vnamey + 25)

  start_x, start_y = v[0], v[1]
  current_y = start_y
  screenshot_index = 1
  found_variant = False

  while not found_variant:
      current_x = start_x
      extracted_info = capture_variant(current_x, current_y)
      if variant_name.lower() in extracted_info.lower():
          print(f"Variant found at ({current_x}, {current_y}) -> '{extracted_info}'")
          pyautogui.click(current_x, current_y)
          found_variant = True
          break
      screenshot_index += 1

      # Scan horizontally
      prev_extracted = extracted_info
      while True:
          current_x += d
          extracted_info = capture_variant(current_x, current_y, wait_time, vname_area, screenshot_index)
          if debug:
            print(f"OCR at ({current_x}, {current_y}): '{extracted_info}'")
          if extracted_info == prev_extracted:  # End horizontal scan if no change
              break
          if variant_name.lower() in extracted_info.lower():
              print(f"Variant found at ({current_x}, {current_y}) -> '{extracted_info}'")
              pyautogui.click(current_x, current_y)
              found_variant = True
              break
          screenshot_index += 1
          prev_extracted = extracted_info
      if found_variant:
          break
      
      # Move down one row
      current_y += d
      new_row_ocr = capture_variant(start_x, current_y, wait_time, vname_area, screenshot_index)
      if new_row_ocr == prev_extracted:
          print("No new variants found in new row. Ending search.")
          break

  if not found_variant:
      print("**ERROR** Variant not found via OCR")
      return False

  return True