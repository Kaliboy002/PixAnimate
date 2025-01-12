import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import InputFile
import cv2
import numpy as np
from PIL import Image, ImageFilter
import io

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Your bot token
TOKEN = '7628087790:AAHHX-BS4qEUwkFm8nlF6aD9XAkxOo1o8tM'

def cartoonize_image(image):
    # Convert PIL image to a NumPy array
    img = np.array(image)
    
    # Convert the image to RGB (OpenCV uses BGR by default)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # Apply bilateral filter to smooth the image while preserving edges
    smoothed = cv2.bilateralFilter(img_rgb, d=9, sigmaColor=50, sigmaSpace=50)
    
    # Convert to grayscale
    gray = cv2.cvtColor(smoothed, cv2.COLOR_BGR2GRAY)
    
    # Apply median blur to reduce noise
    gray = cv2.medianBlur(gray, 7)
    
    # Detect edges using adaptive thresholding
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, blockSize=9, C=2)
    
    # Convert edges back to color
    edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    # Combine edges with the smoothed image
    cartoon = cv2.bitwise_and(smoothed, edges_color)
    
    # Apply unsharp mask to sharpen the image
    cartoon_sharpened = cv2.addWeighted(cartoon, 1.5, cv2.GaussianBlur(cartoon, (0, 0), 1.0), -0.5, 0)
    
    # Convert the result back to PIL Image format
    cartoon_image = Image.fromarray(cv2.cvtColor(cartoon_sharpened, cv2.COLOR_BGR2RGB))

    return cartoon_image

# Start command
async def start(update, context):
    await update.message.reply_text("Send me an image and I'll turn it into a cartoon!")

# Handle images and apply cartoon filter
async def handle_image(update, context):
    photo = await update.message.photo[-1].get_file()  # Get the highest quality image
    image_stream = io.BytesIO()
    await photo.download_to_memory(image_stream)
    
    # Open the image with PIL
    image = Image.open(image_stream)

    # Apply the cartoon filter
    cartoon_image = cartoonize_image(image)
    
    # Save the cartoonized image in memory
    cartoon_stream = io.BytesIO()
    cartoon_image.save(cartoon_stream, format='PNG')
    cartoon_stream.seek(0)
    
    # Send the cartoonized image back
    await update.message.reply_photo(photo=InputFile(cartoon_stream, filename="cartoon.png"))

# Error handling
async def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# Main function to start the bot
def main():
    # Create the Application and pass it the bot's token.
    application = Application.builder().token(TOKEN).build()

    # Command handler for /start
    application.add_handler(CommandHandler("start", start))

    # Handler for images
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    # Log all errors
    application.add_error_handler(error)

    # Start the Bot (run polling)
    application.run_polling()

if __name__ == '__main__':
    main()
