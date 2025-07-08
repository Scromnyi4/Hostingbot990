import logging
import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot configuration
BOT_TOKEN = "7870492055:AAGoM58lacWK2MtjMpNMh3Yqrt47UeZ5HyA"
ALLOWED_CHAT_ID = -1002231017481  # Замените на ID вашей группы (может быть отрицательным для групп)
API1_URL = "https://likes-scromnyi.vercel.app/like"
API1_KEY = "Scromnyimodz999"
API2_URL = "https://community-ffbd.onrender.com/pvlike"

# Global counter for API switching
request_counter = 1

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global request_counter
    
    # Проверяем, что команда отправлена в разрешенном чате
    if update.effective_chat.id != ALLOWED_CHAT_ID:
        await update.message.reply_text("Этот бот работает только в определенной группе!")
        return
    
    # Check if command has correct arguments
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /like <region> <uid>")
        return
    
    region = context.args[0]
    uid = context.args[1]
    
    # Send initial response
    temp_msg = await update.message.reply_text("Got your request, please wait...")
    
    try:
        # Determine which API to use
        use_api1 = (request_counter % 10) < 1 # Alternate every 20 requests
        
        if use_api1:
            # Call API 1 with region
            params = {
                'uid': uid,
                'region': region,
                'key': API1_KEY
            }
            response = requests.get(API1_URL, params=params)
            data = response.json()
            
            # Process API 1 response
            if data.get('status') == 1:
                message = (
                    f"✅ Likes Sent\n"
                    f"Player Name: {data.get('PlayerNickname', 'N/A')}\n"
                    f"UID: {data.get('UID', 'N/A')}\n"
                    f"Likes Before: {data.get('LikesBeforeCommand', 'N/A')}\n"
                    f"Likes Given: {data.get('LikesGivenByAPI', 'N/A')}\n"
                    f"Likes After: {data.get('LikesAfterCommand', 'N/A')}"
                )
            else:
                message = "Player has reached max likes today!"
            
        else:
            # Call API 2 without region
            params = {'uid': uid}
            response = requests.get(API2_URL, params=params)
            data = response.json()
            
            # Check for token refresh message
            if isinstance(data, str) and "Token is being refreshed" in data:
                message = "Service is refreshing, please try again later!"
            else:
                # Process API 2 response
                likes_given = data.get('LikesGivenByAPI', 0)
                
                if likes_given == 0:
                    message = "Player has reached max likes today!"
                else:
                    message = (
                        f"✅ Likes Sent\n"
                        f"Player Name: {data.get('PlayerNickname', 'N/A')}\n"
                        f"UID: {data.get('UID', 'N/A')}\n"
                        f"Likes Before: {data.get('LikesbeforeCommand', data.get('LikesBefore', 'N/A'))}\n"
                        f"Likes Given: {likes_given}\n"
                        f"Likes After: {data.get('LikesafterCommand', data.get('LikesAfter', 'N/A'))}"
                    )
        
        # Increment request counter
        request_counter += 1
        
        # Delete the "please wait" message after 5 seconds
        time.sleep(5)
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=temp_msg.message_id
        )
        
        # Send the result
        await update.message.reply_text(message)
        
    except Exception as e:
        logging.error(f"Error processing like command: {e}")
        await update.message.reply_text("An error occurred while processing your request.")

def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handler
    application.add_handler(CommandHandler("like", like_command))
    
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
