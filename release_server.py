import os
import time
import traceback
import requests
from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import tempfile
from  dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Telegram Bot Token (Replace with your actual token)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Global variables to store user data
user_data = {}

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Welcome to Face Swap Bot!\n"
        "1. Send the first photo (face to swap)\n"
        "2. Send the second photo (face to swap onto)\n"
        "I'll then process them and send back the result!"
    )

async def handle_photo(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    
    # Create user directory if it doesn't exist
    if user_id not in user_data:
        user_data[user_id] = {
            'step': 1,
            'temp_dir': tempfile.mkdtemp(),
            'chat_id': chat_id
        }
    
    # Get the highest resolution photo
    photo = update.message.photo[-1]
    file_id = photo.file_id
    bot = context.bot
    
    # Download the photo
    photo_file = await bot.get_file(file_id)
    timestamp = str(int(time.time()))
    
    if user_data[user_id]['step'] == 1:
        # First photo (source image)
        file_path = os.path.join(user_data[user_id]['temp_dir'], f"source_{timestamp}.png")
        await photo_file.download_to_drive(file_path)
        user_data[user_id]['source_image'] = file_path
        user_data[user_id]['step'] = 2
        await update.message.reply_text("First photo received! Now please send the second photo.")
    elif user_data[user_id]['step'] == 2:
        # Second photo (target image)
        file_path = os.path.join(user_data[user_id]['temp_dir'], f"target_{timestamp}.png")
        await photo_file.download_to_drive(file_path)
        user_data[user_id]['target_image'] = file_path
        await update.message.reply_text("Second photo received! Processing face swap...")
        
        # Process face swap
        await process_face_swap(user_id, bot)

async def process_face_swap(user_id, bot):
    try:
        data = user_data[user_id]
        SOURCE_IMAGE_PATH = data['source_image']
        TARGET_IMAGE_PATH = data['target_image']
        chat_id = data['chat_id']
        
        # Verify files exist
        if not os.path.exists(SOURCE_IMAGE_PATH):
            bot.send_message(chat_id, "Error: Source image not found.")
            return
        if not os.path.exists(TARGET_IMAGE_PATH):
            bot.send_message(chat_id, "Error: Target image not found.")
            return

        url = "https://deepimg.ai/ai-face-swap/#Generate-box"
        result_image_path = None

        try:
            # Initialize driver (UC mode with headless)
            driver = Driver(
                browser="chrome",
                headless=True,
                no_sandbox=True,
                disable_gpu=True,
                incognito=True,
                uc=True,
            )
            wait = WebDriverWait(driver, 30)
            await bot.send_message(chat_id, "Starting face swap process... (wait for 2-3 minutes)")
            driver.open_url(url)
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
            result_image_path = os.path.join(data['temp_dir'], f"result_{int(time.time())}.png")

            while attempt < max_attempts:
                try:
                    result_img = driver.find_element(By.XPATH, "/html/body/div[3]/section[2]/div/div/div/div[1]/img[2]")
                    img_src = result_img.get_attribute("src")
                    time.sleep(2)

                    response = requests.get(img_src)
                    if response.status_code == 200:
                        with open(result_image_path, "wb") as f:
                            f.write(response.content)
                        break
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(15)
                    attempt += 1

            if attempt >= max_attempts:
                await bot.send_message(chat_id, "Face swap did not complete within the expected time")
                return

            # Send the result image
            with open(result_image_path, 'rb') as photo:
                await bot.send_photo(chat_id, photo, caption="Here's your face swap result!")
            
        except Exception as e:
            await bot.send_message(chat_id, f"An error occurred during processing: {str(e)}")
            traceback.print_exc()
        finally:
            if 'driver' in locals():
                driver.quit()
            
    except Exception as e:
        await bot.send_message(chat_id, f"An unexpected error occurred: {str(e)}")
        traceback.print_exc()
    finally:
        # Clean up temporary files
        if user_id in user_data:
            temp_dir = user_data[user_id]['temp_dir']
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")
                try:
                    os.rmdir(temp_dir)
                except Exception as e:
                    print(f"Error deleting directory {temp_dir}: {e}")
            del user_data[user_id]

async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors caused by updates."""
    print(f'Update {update} caused error {context.error}')
    if update is not None and hasattr(update, 'message') and update.message:
        await update.message.reply_text('An error occurred. Please try again.')

def main():
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_error_handler(error_handler)

    # Start the Bot
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()