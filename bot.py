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
ALLOWED_CHAT_ID = [-1002231017481,-1002653911532]
ADMIN_ID = 8074368052  # ID администратора
API1_URL = "https://likes-scromnyi.vercel.app/like"
API1_KEY = "sk_5a6bF3r9PxY2qLmZ8cN1vW7eD0gH4jK"
API2_URL = "https://community-ffbd.onrender.com/pvlike"

# Global variables for API switching
current_api = 1  # 1 for API1, 2 for API2

async def is_admin(update: Update) -> bool:
    """Проверяет, является ли отправитель администратором"""
    return update.effective_user.id == ADMIN_ID

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что команда отправлена в разрешенном чате
    if update.effective_chat.id not in ALLOWED_CHAT_ID:
        await update.message.reply_text("Этот бот работает только в определенной группе!")
        return
    
    # Check if command has correct arguments
    if len(context.args) < 2:
        await update.message.reply_text("")
        return
    
    region = context.args[0]
    uid = context.args[1]
    
    # Send initial response
    temp_msg = await update.message.reply_text("Got your request, please wait...")
    
    try:
        if current_api == 1:
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
                    f"Likes Sent ✅\n"
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
                    message = "Player has reached max likes today."
                else:
                    message = (
                        f"✅ Likes Sent\n"
                        f"Player Name: {data.get('PlayerNickname', 'N/A')}\n"
                        f"UID: {data.get('UID', 'N/A')}\n"
                        f"Likes Before: {data.get('LikesbeforeCommand', data.get('LikesBefore', 'N/A'))}\n"
                        f"Likes Given: {likes_given}\n"
                        f"Likes After: {data.get('LikesafterCommand', data.get('LikesAfter', 'N/A'))}"
                    )
        
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

async def set_api_ratio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_api
    
    # Проверяем, что команда отправлена администратором
    if not await is_admin(update):
        await update.message.reply_text("⛔ Эта команда доступна только администратору!")
        return
    
    # Проверяем, что команда отправлена в разрешенном чате
    if update.effective_chat.id not in ALLOWED_CHAT_ID:
        await update.message.reply_text("Этот бот работает только в определенной группе!")
        return
    
    # Check if command has correct arguments
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /setapi <1 or 2>\nExample: /setapi 1 - использовать первый API\n/setapi 2 - использовать второй API")
        return
    
    try:
        api_choice = int(context.args[0])
        if api_choice in [1, 2]:
            current_api = api_choice
            await update.message.reply_text(f"✅ API switched to {'first' if current_api == 1 else 'second'} API")
        else:
            await update.message.reply_text("Please enter 1 or 2\n1 - первый API\n2 - второй API")
    except ValueError:
        await update.message.reply_text("Invalid value. Please provide 1 or 2\n1 - первый API\n2 - второй API")

def main():
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("like", like_command))
    application.add_handler(CommandHandler("setapi", set_api_ratio))
    
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
