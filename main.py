from seleniumbase import Driver
import time
import traceback
import os
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Get absolute paths to the images
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_IMAGE_PATH = os.path.join(SCRIPT_DIR, "2.png")  # The face you want to swap
TARGET_IMAGE_PATH = os.path.join(SCRIPT_DIR, "5.jpg")  # The face you want to swap onto

# Verify files exist
if not os.path.exists(SOURCE_IMAGE_PATH):
    raise FileNotFoundError(f"Source image not found at: {SOURCE_IMAGE_PATH}")
if not os.path.exists(TARGET_IMAGE_PATH):
    raise FileNotFoundError(f"Target image not found at: {TARGET_IMAGE_PATH}")

url = "https://deepimg.ai/ai-face-swap/#Generate-box"

try:
    # Initialize driver (UC mode with headless)
    driver = Driver(uc=True, headless=True)
    wait = WebDriverWait(driver, 30)
    
    print("Opening URL...")
    driver.uc_open_with_reconnect(url, 1)
    
    # Wait for page to load
    print("Waiting for page to load...")
    time.sleep(5)
    
    # Upload first image
    print(f"Uploading source image from: {SOURCE_IMAGE_PATH}")
    source_input = wait.until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[3]/section[2]/div/div/form/div[1]/div[1]/div/input")
    ))
    source_input.send_keys(SOURCE_IMAGE_PATH)
    print("Source image uploaded, waiting for processing...")
    time.sleep(5)  # Wait for processing
    
    # Upload second image
    print(f"Uploading target image from: {TARGET_IMAGE_PATH}")
    target_input = wait.until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[3]/section[2]/div/div/form/div[1]/div[2]/div/input")
    ))
    target_input.send_keys(TARGET_IMAGE_PATH)
    print("Target image uploaded, waiting for processing...")
    time.sleep(5)  # Wait for processing
    
    # Click the face swap button
    print("Starting face swap...")
    swap_button = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div[3]/section[2]/div/div/form/div[2]/button")
    ))
    swap_button.click()
    print("Face swap process started...")
    
    # Wait for result and download
    print("Waiting for face swap to complete...")
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # /html/body/div[3]/section[2]/div/div/div/button
            download_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[3]/section[2]/div/div/div/button")
            ))
            # Wait for result image to appear
            result_img = wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[3]/section[2]/div/div/div/div[1]/img[2]")
            ))

            try:
                # Get the base64 image data
                img_src = result_img.get_attribute("src")
                time.sleep(2)  # Ensure the image is fully loaded
                #save the image downloaded via url
                response = requests.get(img_src)
                if response.status_code == 200:
                    with open(f"result_{time.time()}.png", "wb") as f:
                        f.write(response.content)
                    print("Result image saved as 'result.png'")
                else:
                    print(f"Failed to retrieve image from URL: {img_src}")
            except Exception as img_error:
                print(f"Error saving result image: {img_error}")
            
            # then press /html/body/div[3]/section[2]/div/div/div/button
            # download_button = wait.until(EC.element_to_be_clickable(
            #     (By.XPATH, "/html/body/div[3]/section[2]/div/div/div/button")
            # ))
            # download_button.click()
            print("Download button clicked, waiting for download to complete...")
            # time.sleep(10)  # Wait for download to complete
            print("Face swap completed! Please check the result on the website.")
            break
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(15)
            attempt += 1
    
    if attempt >= max_attempts:
        print("Face swap did not complete within the expected time")
    
    driver.quit()
    
except Exception as e:
    print("An error occurred:")
    traceback.print_exc()
    if 'driver' in locals():
        driver.quit()