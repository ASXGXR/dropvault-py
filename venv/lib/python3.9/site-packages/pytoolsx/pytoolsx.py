import smtplib
import ssl
from email.message import EmailMessage
import ssl #mail
import smtplib #mail
import time
import pyautogui
from PIL import Image, ImageOps
import pytesseract
from pytesseract import image_to_data, Output
import ast
try:
    import beepy
except:
    pass
from pynput.mouse import Listener, Controller
import tkinter as tk

# ========================
# Communication Functions
# ========================

def send_mail(subject, body, email_receiver='alexsagar13@gmail.com',
              email_sender = 'ceostockgrabber@gmail.com',
              email_password = ''):
    """Sends an email to the specified receiver with the given subject and body."""
    sendmail_counter = 0
    sendmail_max_count = 5
    while sendmail_counter < sendmail_max_count:
        try:
            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
                print(f"[Email sent to {email_receiver}]")

            sendmail_counter = sendmail_max_count
        except Exception as e:
            print(f"Unable to send email, retrying.. Error: {e}")
            time.sleep(5)
            sendmail_counter += 1


# =====================
# Movement Functions
# =====================

def pos():
    """Prints the current position of the mouse cursor."""
    x, y = pyautogui.position()
    print(f"({x}, {y})")

def moveClick(x, y=None, time_wait=1):
    """Moves the mouse to the specified position and performs a click."""
    # Extract (x, y) coordinates if x is a tuple or list
    if isinstance(x, (tuple, list)):
        x, y = x[0], x[1]
    elif isinstance(x, str) and x.lower() in {"center", "mid"}:
        screen_width, screen_height = pyautogui.size()
        x, y = screen_width // 2, screen_height // 2
    elif y is None:
        raise ValueError("If 'x' is not a list, tuple, or 'center', both 'x' and 'y' must be specified.")
    
    # Move and click at the determined (x, y) position
    pyautogui.moveTo(x, y, time_wait)
    time.sleep(0.6)
    pyautogui.click(x, y)

def tryExcept(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        return e

def recordClicks(duration=4):
    """Records mouse clicks over a specified duration."""
    events = []  # List to store click events, with a consistent structure
    def on_click(x, y, button, pressed):
        if pressed:  # Record on button press
            events.append({'type': 'click', 'pos': (x, y), 'time': round(time.time() - stime, 3)})
    print("Recording clicks in..")
    for i in range(1, 4):
        print(4 - i)
        time.sleep(0.4)
    try:
        beepy.beep(sound=1)  # Start recording beep
    except:
        pass
    stime = time.time()  # Start time
    with Listener(on_click=on_click) as listener:
        while time.time() - stime < duration:
            pass  # Keep the listener active until the duration is up
        listener.stop()
    try:
        beepy.beep(sound=1)  # End recording beep
    except:
        pass
    return events

def recordMouse(duration=4):
    """Records mouse events including movements and clicks over a specified duration."""
    events = []  # Combined list for both moves and clicks
    mouse = Controller()
    def on_click(x, y, button, pressed):
        if pressed:  # Record only on button press, not release
            events.append({'type': 'click', 'pos': (x, y), 'time': round(time.time() - stime, 3)})
    print("Recording mouse in..")
    for i in range(1, 4):
        print(4 - i)
        time.sleep(0.4)
    beepy.beep(sound=1)  # Start recording beep
    with Listener(on_click=on_click) as listener:
        stime = time.time()  # Start time
        while time.time() - stime < duration:
            events.append({'type': 'move', 'pos': mouse.position, 'time': round(time.time() - stime, 3)})
            time.sleep(0.1)  # Interval between position recordings
        listener.stop()
    beepy.beep(sound=1)  # End recording beep
    return events

def playMouse(events,speed=1):
    """Replays recorded mouse events with smooth transitions."""
    stime = time.time()  # Start time for playback
    last_event_time = 0  # Initialize last event time
    for event in sorted(events, key=lambda x: x['time']):
        wait_time = (event['time'] / speed) - last_event_time
        pyautogui.moveTo(event['pos'][0], event['pos'][1], duration=wait_time)
        if event['type'] == 'click':
            pyautogui.click(event['pos'][0], event['pos'][1])
        last_event_time = event['time'] / speed
        
            
# ======================
# Imaging / OCR Functions
# ======================

def findOnPage(target_text, debug=False, invert=False, loop=False):
    """Finds text on a page, outputs the coordinates"""
    while True:
        screenshot = pyautogui.screenshot().convert("RGB")
        if invert:
            screenshot = ImageOps.invert(screenshot)
        data = image_to_data(screenshot, output_type=Output.DICT)
        for i, text in enumerate(data['text']):
            if text.strip().lower() == target_text.lower():
                coords = (data['left'][i] + data['width'][i] // 2, data['top'][i] + data['height'][i] // 2)
                if debug:
                    print(f"Text found at: {coords}")
                return coords
        if not loop:
            if debug:
                print(f"Text '{target_text}' not found.")
            return None

def clickFindOnPage(target_text, debug=False, invert=False, loop=False):
    """Finds and clicks on the specified text on a page."""
    coords = findOnPage(target_text, debug=debug, invert=invert, loop=loop)
    if coords:
        if debug:
            print(f"Clicking at coordinates: {coords}")
        pyautogui.moveTo(coords)
        pyautogui.click()
        return True
    if debug:
        print(f"Unable to click. Text '{target_text}' not found.")
    return False

def newOcr(region,invert="no"):
    screenshot = pyautogui.screenshot(region=region).convert('L')
    if invert=="yes":
        screenshot = ImageOps.invert(screenshot)
    binarized_image = screenshot.resize((screenshot.width * 2, screenshot.height * 2), Image.Resampling.LANCZOS)
    binarized_image = binarized_image.point(lambda x: 0 if x < 128 else 255, '1')
    text = pytesseract.image_to_string(binarized_image).strip().lower()
    return text

def ocr(x1=0, y1=0, x2=1920, y2=1080, binarize="no", save="no", thresh=80):
    """Performs OCR on a screenshot taken from the specified screen region."""
    if isinstance(x1, list) and len(x1) == 4:
        x1, y1, x2, y2 = x1
    try:
        image = pyautogui.screenshot(region=(int(x1), int(y1), int(x2-x1), int(y2-y1)))
        if binarize == "yes":
            image = image.convert('L')
            image = image.point(lambda p: p > thresh and 255)
            image = ImageOps.invert(image)
        if save == "yes":
            image.save("ss.png")
        ocr_text = pytesseract.image_to_string(image)
    except Exception as e:
        print(f"Error occurred scanning or taking screenshot: {e}")
        ocr_text = ""
    return ocr_text.lower()

def screenshot(filename="ss.png"):
    """Takes and saves a screenshot, defaults to ss.png."""
    while True:
        try:
            if ".png" not in filename:
                filename += ".png"
            image = pyautogui.screenshot()
            image.save(filename)
            break
        except Exception as e:
            print("Unable to screenshot:",e)
            time.sleep(5)

def checkForText(target_text, region_coords, click="no", debug="no", invert="no", print_ocr="no"):
    """Checks if text is found in a specified region, clicks if needed"""
    # Take a screenshot of the specified region
    region=(
        region_coords[0][0], 
        region_coords[0][1], 
        region_coords[1][0] - region_coords[0][0], 
        region_coords[1][1] - region_coords[0][1]
    )
    if invert=="yes":
        text=newOcr(region,invert="yes")
    else:
        text=newOcr(region)
    # Debugging output
    if print_ocr == "yes" or debug.lower() == "yes":
        print("OCR Result:", text)  # Prints the text extracted by OCR
    if debug.lower() == "yes":
        screenshot.show()  # Opens the screenshot in the default image viewer
    # Check if the target text is in the OCR result
    if target_text.lower() in text.lower():
        if click.lower() == "yes":
            mid_x = (region_coords[0][0] + region_coords[1][0]) // 2
            mid_y = (region_coords[0][1] + region_coords[1][1]) // 2
            pyautogui.click(mid_x, mid_y)
            if debug == "yes": print(f"Clicked at ({mid_x}, {mid_y})")
        return True
    return False

def draw_box(x1, y1, x2, y2):
    root = tk.Tk()
    root.attributes('-alpha', 0.3, '-topmost', True)
    canvas = tk.Canvas(root, width=round(x2-x1), height=round(y2-y1))
    canvas.create_rectangle(0, 0, round(x2-x1), round(y2-y1), outline='red')
    canvas.pack()
    root.geometry(f'+{round(x1)}+{round(y1)}')
    root.after(1000, root.destroy)
    root.mainloop()

def panelFind(item, tlc, brc, search_from="above", search_step=2, panel_items=10,
              print_ocr="no", binarize="no", scrollTo="yes",drawBox="no",
              save="no"):
    """Searches for an item within a specified panel area using OCR."""
    item = item.replace(" ", "").lower() # lowercase + removes spaces

    # where to click once found
    distance_frac = 1/8
    ideal_pos = [round(tlc[i] + (brc[i] - tlc[i]) * distance_frac) for i in (0, 1)]

    box_width = (brc[1] - tlc[1]) / panel_items
    area = [tlc[0], brc[1] - box_width if search_from == "below" else tlc[1], brc[0], brc[1] if search_from == "below" else tlc[1] + box_width]
    search_step *= -1 if search_from == "below" else 1
    def search_area(step):
        return [area[0], area[1] + step, area[2], area[3] + step]

    counter, not_found_count, coord_list, item_found = -1, 0, [], "no"
    while not_found_count < 2:
        counter += 1
        step = counter * search_step
        if drawBox=="yes":
            draw_box(*search_area(step))
        ocr_text = textOnly(ocr(*search_area(step), binarize=binarize, save=save)).replace("\n", "").replace(" ", "")
        if print_ocr == "yes": print(ocr_text)
        if item in ocr_text: item_found = "yes"
        if area[3] + step > brc[1] or area[1] + step < tlc[1]:
            if scrollTo == "yes":
                pyautogui.moveTo(*ideal_pos, 0.5) # Scroll if out of bounds
                pyautogui.scroll(-200 if search_from == "above" else 200)
                counter = -1  # Reset counter
            else:
                break
        if item_found == "yes":
            mid_y = (area[1] + area[3] + step * 2) / 2
            coord_list.append(mid_y)
            not_found_count = 0 if item in ocr_text else not_found_count + 1
    coord_list = coord_list[:-2]  # Remove last two coordinates after not finding the item

    if coord_list:
        if print_ocr == "yes":
            print(coord_list)
            print(f"Found {item}!")
        item_y = round(sum(coord_list) / len(coord_list))
        if scrollTo == "yes":
            pyautogui.moveTo(*ideal_pos, 0.5)
            time.sleep(0.5)
            pyautogui.scroll(int(round(ideal_pos[1] - item_y, 0)))
            time.sleep(0.5)
            pyautogui.click(*ideal_pos)
        else:
            ideal_pos = [(tlc[0]+brc[0])/2, item_y]
    return ideal_pos

def panelFindStatic(top_left, bottom_right, num_items, desired_text, invert=False, debug_mode=False):
    """Searches for an item in a static list, based on a given number of items"""
    x1, y1 = top_left
    x2, y2 = bottom_right
    panel_width, item_height = x2 - x1, (y2 - y1) / num_items

    if debug_mode:
        os.makedirs("debug_images", exist_ok=True)

    for i in range(num_items):
        top = y1 + int(i * item_height)
        region = (x1, top, panel_width, int(item_height))
        screenshot = pyautogui.screenshot(region=region).convert('L')
        binarized_image = ImageOps.invert(screenshot)
        binarized_image = binarized_image.resize((binarized_image.width * 2, binarized_image.height * 2), Image.Resampling.LANCZOS)
        binarized_image = binarized_image.point(lambda x: 0 if x < 128 else 255, '1')
        text = pytesseract.image_to_string(binarized_image).strip().lower()

        if debug_mode:
            binarized_image.save(f"debug_images/item_{i+1}.png")
            print(f"Item {i+1}: {text}")

        if desired_text.lower() in text:
            pyautogui.click(x=x1 + panel_width // 2, y=top + int(item_height // 2))
            print(f"Found '{desired_text}' in item {i+1}, clicked.")
            break
            

# ========================
# Text Manipulation Functions
# ========================

def textOnly(t, exception=""):
    """Returns a string containing only alphabetic characters and spaces from the given string."""
    text_only = "".join(char for char in t if char.isalpha() or char.isspace() or char == exception)
    return text_only

def numOnly(n, exception=""):
    """Returns a string containing only numeric characters from the given string."""
    num_only = "".join(char for char in n if char.isnumeric() or char == '.' or char == exception)
    return num_only

def removeAfter(string, remove):
    """Returns a substring from the beginning of the given string to the first occurrence of the specified marker."""
    new_str = string.split(remove)[0]
    return new_str

def removeBefore(string, remove):
    """Returns a substring from the first occurrence of the specified marker to the end of the given string."""
    try:
        new_str = string.split(remove)[1]
        return new_str
    except IndexError:
        return string


# =======================
# List Manipulation Functions
# =======================

def removeListBefore(lst, remove):
    """Returns a new list containing elements after the specified value in the given list."""
    index = lst.index(remove)
    new_list = lst[index + 1:]
    return new_list

def removeListAfter(lst, remove):
    """Returns a new list containing elements up to and including the specified value in the given list."""
    new_list = lst[:lst.index(remove) + 1]
    return new_list


# =======================
# File Manipulation Functions
# =======================

def dictsFromFile(filename):
    """Reads a list of dictionaries from a text file."""
    if ".txt" not in filename:
        filename += ".txt"
    dict_list = []
    with open(filename, "r") as file:
        for line in file:
            if line.strip():  # Check if the line is not empty or contains only whitespaces
                dict_list.append(ast.literal_eval(line))
    return dict_list

def dictsToFile(filename, dictList):
    """Writes a list of dictionaries to a text file."""
    if ".txt" not in filename:
        filename += ".txt"
    with open(filename, "w") as file:
        for d in dictList:
            file.write(str(d) + '\n')


# =======================
# System Functions
# =======================

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

def set_volume(level):
    # Get default audio device
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)

    # Normalize the level to the range [0.0, 1.0]
    volume.SetMasterVolumeLevelScalar(level / 100.0, None)
    print(f"System Volume set to {level}")

