import os
import sys
import time
import requests
import pyautogui
import cv2
import numpy as np
from io import BytesIO
from skimage.metrics import structural_similarity as ssim
from PIL import Image, ImageChops, ImageOps
from pytesseract import image_to_data, Output
import pytoolsx as pt

def select_variant(ebay_url, variant_name):

    debug = False

    # -----------------------------------------------------------------------------
    # 1) Load Reference Image (eBay)
    # -----------------------------------------------------------------------------
    response = requests.get(ebay_url)
    ebay_v_image = Image.open(BytesIO(response.content)).convert('RGB')

    # Convert eBay image to OpenCV format
    ebay_v_image = np.array(ebay_v_image)
    ebay_v_image = cv2.cvtColor(ebay_v_image, cv2.COLOR_RGB2BGR)  # Convert to BGR for OpenCV

    # Get reference image dimensions
    ref_height, ref_width = ebay_v_image.shape[:2]

    # -----------------------------------------------------------------------------
    # 2) Define Similarity Functions
    # -----------------------------------------------------------------------------
    def resize_image(image, width, height):
        """Resize image to match the reference image dimensions."""
        return cv2.resize(image, (width, height))

    def compute_ssim(imageA, imageB):
        """Compute Structural Similarity Index (SSIM) between two images."""
        imageA = resize_image(imageA, ref_width, ref_height)  # Resize before SSIM
        imageB = resize_image(imageB, ref_width, ref_height)
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
        score, _ = ssim(grayA, grayB, full=True)
        return score

    def compute_rmse(imageA, imageB):
        """Compute Root Mean Square Error (RMSE) between two images."""
        imageA = resize_image(imageA, ref_width, ref_height)
        imageB = resize_image(imageB, ref_width, ref_height)
        error = np.sqrt(np.mean((imageA - imageB) ** 2))
        return error

    def compute_psnr(imageA, imageB):
        """Compute Peak Signal-to-Noise Ratio (PSNR)."""
        imageA = resize_image(imageA, ref_width, ref_height)
        imageB = resize_image(imageB, ref_width, ref_height)
        return cv2.PSNR(imageA, imageB)

    def ocr(region, invert=False, debug=False):
        """Performs OCR on a given region and returns detected text as a single string."""
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

    # -----------------------------------------------------------------------------
    # 3) Setup Screenshot Directory
    # -----------------------------------------------------------------------------
    screenshot_dir = "variant_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    # -----------------------------------------------------------------------------
    # 4) Find AliExpress Variant Region
    # -----------------------------------------------------------------------------
    x1, y1 = 177, 324
    x2, y2 = 772, 922
    region = (x1, y1, x2 - x1, y2 - y1)

    # Find "Color:" label on the page
    ali_ref = pt.findOnPage(["Color:","Name:"], loop=True)
    v = [ali_ref[0] - 20, ali_ref[1] + 60]  # first variant position
    vnamex, vnamey = ali_ref
    vname_area = (vnamex - 50, vnamey - 25, vnamex + 300, vnamey + 25)

    # --------------------------------------------------------------------------
    # 5) Collect Screenshots by Clicking Variants
    # --------------------------------------------------------------------------
    def capture_variant(current_x, current_y, wait_time, region, screenshot_dir, screenshot_index):
        """Clicks, optionally does an extra click if index==14, waits, captures, saves, and converts a screenshot."""
        pyautogui.click(current_x, current_y)
        if screenshot_index == 14:
            time.sleep(wait_time)
            pyautogui.click(current_x, current_y)
        time.sleep(wait_time)
        # Check if variant name matches using OCR on the variant name area (vname_area)
        extracted_info = ocr(vname_area)
        boost = False
        if variant_name.lower() in extracted_info.lower():
            boost = True  # Boost this variant in the similarity metrics
        ss = pyautogui.screenshot(region=region)
        ss_path = os.path.join(screenshot_dir, f"variant_{screenshot_index}.png")
        if debug:
            ss.save(ss_path)
        screenshot_index += 1
        ss_cv = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2BGR)
        return ss, ss_cv, ss_path, screenshot_index, boost

    screenshots = []
    start_x, start_y = v[0], v[1]
    current_y = start_y
    d = 110  # Distance between variant boxes
    last_ss = None
    screenshot_index = 1
    wait_time = 1.1  # Time between clicks

    while True:
        current_x = start_x
        ss, ss_cv, ss_path, screenshot_index, boost = capture_variant(current_x, current_y, wait_time, region, screenshot_dir, screenshot_index)
        if last_ss and ImageChops.difference(ss, last_ss).getbbox() is None:
            break # If identical to previous ss, stop
        screenshots.append((ss_cv, (current_x, current_y), ss_path, boost))
        last_ss = ss.copy()

        # Scan horizontally in this row
        prev_horiz_ss = ss.copy()
        while True:
            current_x += d
            ss, ss_cv, ss_path, screenshot_index, boost = capture_variant(current_x, current_y, wait_time, region, screenshot_dir, screenshot_index)
            if ImageChops.difference(ss, prev_horiz_ss).getbbox() is None:
                break
            screenshots.append((ss_cv, (current_x, current_y), ss_path, boost))
            prev_horiz_ss = ss.copy()
        # Move down to next row
        current_y += d


    # -----------------------------------------------------------------------------
    # 6) Compare Images and Print Differences
    # -----------------------------------------------------------------------------
    if debug:
        print("\nSimilarity Metrics:")

    # Define weights for each metric (adjust as needed)
    w_ssim = 0.6  # SSIM has the highest priority
    w_rmse = 0.2  # Lower RMSE is better
    w_psnr = 0.2  # Higher PSNR is better

    # Normalize RMSE so lower is better (invert it)
    def normalize_rmse(rmse):
        return 1 / (1 + rmse)  # Keeps values in (0,1) range

    best_match = None
    best_score = -1
    best_coords = None
    best_path = None

    for i, (shot_cv, coords, path, boost) in enumerate(screenshots, start=1):
        ssim_score = compute_ssim(ebay_v_image, shot_cv)
        rmse_score = compute_rmse(ebay_v_image, shot_cv)
        psnr_score = compute_psnr(ebay_v_image, shot_cv)
        
        combined_score = (w_ssim * ssim_score) + (w_rmse * normalize_rmse(rmse_score)) + (w_psnr * (psnr_score / 20))
        if boost:
            combined_score += 10  # Apply a massive boost if variant name matched
        
        if debug:
            print(f"Variant {i} at {coords} -> SSIM: {ssim_score:.4f}, RMSE: {rmse_score:.2f}, PSNR: {psnr_score:.2f}, Combined Score: {combined_score:.4f}")
        if combined_score > best_score:
            best_score = combined_score
            best_match = shot_cv
            best_coords = coords
            best_path = path

    # -----------------------------------------------------------------------------
    # 7) Find Best Match Based on SSIM
    # -----------------------------------------------------------------------------
    threshold = 0.60 # Adjust as needed

    if best_score >= threshold:
        print(f"\nBest variant found at {best_coords} with SSIM: {best_score:.4f}")
        if debug:
            print(f"Best match screenshot saved at: {best_path}")
        pyautogui.click(best_coords[0], best_coords[1])
        return True
    else:
        print(f"\n**ERROR** No variant meets the threshold. Best SSIM: {best_score:.4f} at {best_coords}")
        print(f"Best match screenshot saved at: {best_path}")
        return False