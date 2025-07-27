import logging
import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot configuration
BOT_TOKEN = "8275158418:AAEhTw0NG9QzVvxkPoqYdKVPC2PAGpaeZRc"
ALLOWED_CHAT_ID = [-1002231017481]
ADMIN_ID = 8269775004  # Admin ID
API1_URL = "https://likes-scromnyi.vercel.app/like"
API1_KEY = "ScromnyiDev"
API2_URL = "https://community-ffbd.onrender.com/pvlike"
API3_URL = "https://community-ffbd.onrender.com/like"
API3_KEY = "Scromnyi"
VISIT_API_URL = "http://Community-ffbd.onrender.com/visit?uid="
CHANNEL_ID = "@scromnyi_leaks"  # Каналдын ID же username

# Global variables
current_api = 1
vip_users = set()

async def is_admin(update: Update) -> bool:
    """Check if the sender is an admin"""
    return update.effective_user.id == ADMIN_ID

async def is_vip_or_admin(update: Update) -> bool:
    """Check if the sender is a VIP or admin"""
    return update.effective_user.id in vip_users or await is_admin(update)

async def check_membership(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """Check if the user is a member of the channel"""
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Error checking membership: {e}")
        return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command and prompt for channel subscription"""
    user_id = update.effective_user.id
    if await check_membership(context, user_id):
        await update.message.reply_text(
            "Привет! Используй наш команда:\n"
            "/visit <uid> - 1000 визит жөнөтүү\n"
            "/vipvisit <uid> - VIP визит (VIP үчүн)\n"
            "/like <region> <uid> - Лайк жөнөтүү",
            parse_mode='Markdown'
        )
    else:
        keyboard = [[InlineKeyboardButton("Каналга катталуу", url="https://t.me/scromnyi_leaks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Чтобы использовать бота, подпишитесь на наш канал.",
            reply_markup=reply_markup
        )

async def visit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ALLOWED_CHAT_ID:
        await update.message.reply_text("Этот бот работает только в определенной группе!")
        return

    if not await check_membership(context, update.effective_user.id):
        keyboard = [[InlineKeyboardButton("Подписка на канал.", url="https://t.me/scromnyi_leaks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Чтобы использовать бота, подпишитесь на наш канал.",
            reply_markup=reply_markup
        )
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /visit <uid>")
        return

    uid = context.args[0]
    temp_msg = await update.message.reply_text("Got your visit request, please wait...")

    try:
        response = requests.get(f"{VISIT_API_URL}{uid}")
        data = response.json()
        token_count = data.get('Token Count', 'N/A')
        if "Done" in data.get('message', ''):
            if token_count == 'N/A' and "Token Count:" in data.get('message', ''):
                try:
                    token_count = data['message'].split("Token Count: ")[1].strip()
                except IndexError:
                    token_count = 'N/A'
            message = (
                f"*⭐ Views Sent Successfully ⭐*\n\n"
                f"*✅ Done.* Successfully Sent 1000 visits to the UID: {uid}. Token Count: {token_count} 🔥\n\n"
                f"*ℹ️ Re-Start* Your Game to Check the Visit Counts in Your Profile! 🙃"
            )
        else:
            message = "Error: Could not send visits. Please try again later."

        time.sleep(5)
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=temp_msg.message_id
        )
        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error processing visit command: {e}")
        await update.message.reply_text("An error occurred while processing your visit request.")

async def vipvisit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_vip_or_admin(update):
        await update.message.reply_text("⛔ Эта команда доступна только для VIP пользователей или администратора!")
        return

    if update.effective_chat.id not in ALLOWED_CHAT_ID:
        await update.message.reply_text("Этот бот работает только в определенной группе!")
        return

    if not await check_membership(context, update.effective_user.id):
        keyboard = [[InlineKeyboardButton("Подписка на канал.", url="https://t.me/scromnyi_leaks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Чтобы использовать бота, подпишитесь на наш канал.",
            reply_markup=reply_markup
        )
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /vipvisit <uid>")
        return

    uid = context.args[0]
    temp_msg = await update.message.reply_text("Got your VIP visit request, please wait...")

    try:
        total_visits = 0
        token_count = 'N/A'

        for _ in range(20):
            response = requests.get(f"{VISIT_API_URL}{uid}")
            data = response.json()

            if "Done" in data.get('message', ''):
                total_visits += 1000
                token_count = data.get('Token Count', 'N/A')
                if token_count == 'N/A' and "Token Count:" in data.get('message', ''):
                    try:
                        token_count = data['message'].split("Token Count: ")[1].strip()
                    except IndexError:
                        token_count = 'N/A'
            else:
                logging.error(f"Failed to send visits for UID {uid} on iteration {_}")
            time.sleep(1)

        if total_visits > 0:
            message = (
                f"*⭐ VIP Views Sent Successfully ⭐*\n\n"
                f"*✅ Done.* Successfully Sent {total_visits} visits to the UID: {uid}. Token Count: {token_count} 🔥\n\n"
                f"*ℹ️ Re-Start* Your Game to Check the Visit Counts in Your Profile! 🙃"
            )
        else:
            message = "Error: Could not send VIP visits. Please try again later."

        time.sleep(5)
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=temp_msg.message_id
        )
        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error processing vipvisit command: {e}")
        await update.message.reply_text("An error occurred while processing your VIP visit request.")

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ALLOWED_CHAT_ID:
        await update.message.reply_text("Этот бот работает только в определенной группе!")
        return

    if not await check_membership(context, update.effective_user.id):
        keyboard = [[InlineKeyboardButton("Подписка на канал.", url="https://t.me/scromnyi_leaks")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            " Чтобы использовать бота, подпишитесь на наш канал.",
            reply_markup=reply_markup
        )
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /like <region> <uid>")
        return

    region = context.args[0]
    uid = context.args[1]
    temp_msg = await update.message.reply_text("Got your request, please wait...")

    try:
        if current_api == 1:
            params = {'uid': uid, 'region': region, 'key': API1_KEY}
            response = requests.get(API1_URL, params=params)
            data = response.json()

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

        elif current_api == 2:
            params = {'uid': uid}
            response = requests.get(API2_URL, params=params)
            data = response.json()

            if isinstance(data, str) and "Token is being refreshed" in data:
                message = "Service is refreshing, please try again later!"
            else:
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

        elif current_api == 3:
            params = {'key': API3_KEY, 'uid': uid, 'region': region}
            response = requests.get(API3_URL, params=params)
            data = response.json()

            if isinstance(data, list) and len(data) >= 2:
                verify_data = data[0]
                status_data = data[1]

                if verify_data.get("verify") == "true":
                    if "Likes Added" in status_data:
                        message = (
                            f"✅ Likes Sent\n"
                            f"Player Name: {status_data.get('Player Name', 'N/A')}\n"
                            f"UID: {status_data.get('Player UID', uid)}\n"
                            f"Likes Before: {status_data.get('Likes Before Command', 'N/A')}\n"
                            f"Likes Given: {status_data.get('Likes Added', 'N/A')}\n"
                            f"Likes After: {status_data.get('Likes after', 'N/A')}"
                        )
                    else:
                        message = "Player has reached max likes for today!"
                else:
                    message = "Verification failed!"
            elif isinstance(data, dict) and data.get("error"):
                message = f"Error:"
            else:
                message = "Something went wrong"

        time.sleep(5)
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=temp_msg.message_id
        )

        await update.message.reply_text(message)

    except Exception as e:
        logging.error(f"Error processing like command with API:")
        await update.message.reply_text("An error occurred while processing your request.")

async def set_api_ratio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_api

    if not await is_admin(update):
        await update.message.reply_text("⛔ Эта команда доступна только администратору!")
        return

    if update.effective_chat.id not in ALLOWED_CHAT_ID:
        await update.message.reply_text("Этот бот работает только в определенной группе!")
        return

    if len(context.args) < 1:
        await update.message.reply_text(
            "Usage: /setapi <1, 2, or 3>\n"
            "Example:\n/setapi 1 - использовать первый API\n"
            "/setapi 2 - использовать второй API\n"
            "/setapi 3 - использовать третий API"
        )
        return

    try:
        api_choice = int(context.args[0])
        if api_choice in [1, 2, 3]:
            current_api = api_choice
            api_names = {1: "first", 2: "second", 3: "third"}
            await update.message.reply_text(f"✅ API switched to {api_names[current_api]} API")
        else:
            await update.message.reply_text(
                "Please enter 1, 2, or 3\n"
                "1 - первый API\n2 - второй API\n3 - третий API"
            )
    except ValueError:
        await update.message.reply_text(
            "Invalid value. Please provide 1, 2, or 3\n"
            "1 - первый API\n2 - второй API\n3 - третий API"
        )

async def vipus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("⛔ Эта команда доступна только администратору!")
        return

    if update.effective_chat.id not in ALLOWED_CHAT_ID:
        await update.message.reply_text("Этот бот работает только в определенной группе!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /vipus <user_id>")
        return

    try:
        user_id = int(context.args[0])
        vip_users.add(user_id)
        await update.message.reply_text(f"✅ User {user_id} has been granted VIP status!")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a valid numeric user ID.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))  # Жаңы /start командасы
    application.add_handler(CommandHandler("like", like_command))
    application.add_handler(CommandHandler("setapi", set_api_ratio))
    application.add_handler(CommandHandler("visit", visit_command))
    application.add_handler(CommandHandler("vipvisit", vipvisit_command))
    application.add_handler(CommandHandler("vipus", vipus_command))
    application.run_polling()

if __name__ == "__main__":
    main()
