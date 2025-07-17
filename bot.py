import logging
import re
import asyncio
import httpx
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from aiogram.enums import ParseMode
from typing import Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "7870492055:AAGoM58lacWK2MtjMpNMh3Yqrt47UeZ5HyA"
ALLOWED_CHAT_IDS = [-1002231017481, -1002653911532]
ADMIN_ID = 8074368052

# API endpoints
API1_URL = "https://likes-scromnyi.vercel.app/like"
API1_KEY = "sk_5a6bF3r9PxY2qLmZ8cN1vW7eD0gH4jK"
API2_URL = "https://community-ffbd.onrender.com/pvlike"
VISIT_API_URL = "http://community-ffbd.onrender.com/visit?uid="
BAN_INFO_URL = "https://ff-bancheck.vercel.app/region/ban-info?uid="
PLAYER_INFO_URL = "https://rzx-team-api-info.vercel.app/info?uid="
BANNER_URL = "https://ff-banner-image.vercel.app/banner-image?uid={uid}&region=sg"
OUTFIT_URL = "https://ff-outfit-image.vercel.app/outfit-image?uid={uid}&region=sg"

# Section headers for formatting
SECTION_HEADERS = {
    "PLAYER INFO", "PLAYER ACTIVITY", "BASIC INFO",
    "PLAYER RANKS", "SOCIAL INFO", "GUILD INFO"
}

# Global variables
current_api = 1  # 1 for API1, 2 for API2
vip_users = set()

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Utility functions
async def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

async def delete_message_with_delay(chat_id: int, message_id: int, delay: int = 5):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

async def clean_and_format_response(text: str) -> str:
    if text.startswith("<pre>") and text.endswith("</pre>"):
        text = text[5:-6].strip()

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if "API INFO OB49" in stripped or "BY API" in stripped:
            continue

        if any(stripped.upper().endswith(header) for header in SECTION_HEADERS):
            cleaned_lines.append(f"<b>{stripped}</b>")
        elif ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                key, value = map(str.strip, parts)
                cleaned_lines.append(f"<b>{key}</b>: {value}")
        else:
            cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)

# Command handlers
@dp.message(Command("start"))
async def start_command(message: types.Message):
    welcome_text = (
        "🌟 <b>Free Fire Bot</b> 🌟\n\n"
        "Available commands:\n"
        "/like <region> <uid> - Send likes\n"
        "/get <uid> - Get player info\n"
        "/visit <uid> - Send 1000 visits\n"
        "/visits <uid> - Send 10k visits (VIP only)\n"
        "/baninfo <uid> - Check ban status\n"
        "/setapi <1|2> - Switch API (Admin only)\n"
        "/allowvisit <user_id> - Add VIP user (Admin only)"
    )
    await message.reply(welcome_text, parse_mode=ParseMode.HTML)

@dp.message(Command("like"))
async def like_command(message: types.Message):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        return await message.reply("❌ This bot works only in specific groups!")
    
    try:
        _, region, uid = message.text.split()
    except ValueError:
        return await message.reply("Usage: /like <region> <uid>")
    
    if not re.fullmatch(r"\d{6,15}", uid):
        return await message.reply("Invalid UID format (6-15 digits)")
    
    temp_msg = await message.reply("🔄 Processing your request...")
    
    try:
        params = {'uid': uid, 'region': region}
        if current_api == 1:
            params['key'] = API1_KEY
            api_url = API1_URL
        else:
            api_url = API2_URL

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, params=params)
            data = response.json()

            if current_api == 1:
                if data.get('status') == 1:
                    result = (
                        f"✅ Likes Sent Successfully\n"
                        f"Name: {data.get('PlayerNickname', 'N/A')}\n"
                        f"UID: {data.get('UID', uid)}\n"
                        f"Before: {data.get('LikesBeforeCommand', 0)}\n"
                        f"Added: {data.get('LikesGivenByAPI', 0)}\n"
                        f"After: {data.get('LikesAfterCommand', 0)}"
                    )
                else:
                    result = "⚠️ Player has reached max likes today!"
            else:
                if isinstance(data, str) and "Token is being refreshed" in data:
                    result = "🔧 Service is refreshing, try again later"
                else:
                    likes_given = data.get('LikesGivenByAPI', 0)
                    result = (
                        f"✅ Likes Sent: {likes_given}\n"
                        f"Name: {data.get('PlayerNickname', 'N/A')}\n"
                        f"UID: {data.get('UID', uid)}"
                    ) if likes_given > 0 else "⚠️ Player has reached max likes today"

        await delete_message_with_delay(message.chat.id, temp_msg.message_id)
        await message.reply(result)

    except Exception as e:
        logger.error(f"Like error: {e}")
        await message.reply("❌ Error processing request")

@dp.message(Command("get"))
async def get_command(message: types.Message):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        return await message.reply("❌ This bot works only in specific groups!")
    
    try:
        _, uid = message.text.split()
    except ValueError:
        return await message.reply("Usage: /get <uid>")
    
    if not re.fullmatch(r"\d{6,15}", uid):
        return await message.reply("Invalid UID format (6-15 digits)")
    
    wait_msg = await message.reply("🔄 Loading player info...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            info_url = f"{PLAYER_INFO_URL}{uid}"
            banner_url = BANNER_URL.format(uid=uid)
            outfit_url = OUTFIT_URL.format(uid=uid)
            
            info_resp, banner_resp, outfit_resp = await asyncio.gather(
                client.get(info_url),
                client.get(banner_url),
                client.get(outfit_url)
            )

            info_resp.raise_for_status()
            banner_resp.raise_for_status()
            outfit_resp.raise_for_status()

            formatted_text = await clean_and_format_response(info_resp.text)
            await message.reply(formatted_text, parse_mode=ParseMode.HTML)
            
            banner_file = BufferedInputFile(banner_resp.content, filename="banner.webp")
            await message.answer_sticker(banner_file)
            
            outfit_file = BufferedInputFile(outfit_resp.content, filename="outfit.png")
            await message.answer_photo(outfit_file)
            
    except httpx.HTTPStatusError as e:
        await message.reply(f"❌ API Error: {e.response.status_code}")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")
    finally:
        await delete_message_with_delay(message.chat.id, wait_msg.message_id, 0)

@dp.message(Command("visit"))
async def visit_command(message: types.Message):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        return await message.reply("❌ This bot works only in specific groups!")
    
    try:
        _, uid = message.text.split()
    except ValueError:
        return await message.reply("Usage: /visit <uid>")
    
    if not re.fullmatch(r"\d{6,15}", uid):
        return await message.reply("Invalid UID format (6-15 digits)")
    
    temp_msg = await message.reply("🔄 Sending visits...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{VISIT_API_URL}{uid}")
            data = response.json()
            
            if "message" in data and "Successfully Sent 1000 visits" in data["message"]:
                token_count = re.search(r"Token Count: (\d+)", data["message"]).group(1)
                result = (
                    f"✅ 1000 Visits Sent\n"
                    f"UID: {uid}\n"
                    f"Tokens Left: {token_count}"
                )
            else:
                result = "❌ Failed to send visits"
        
        await delete_message_with_delay(message.chat.id, temp_msg.message_id)
        await message.reply(result)
        
    except Exception as e:
        logger.error(f"Visit error: {e}")
        await message.reply("❌ Error sending visits")

@dp.message(Command("visits"))
async def visits_command(message: types.Message):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        return await message.reply("❌ This bot works only in specific groups!")
    
    if message.from_user.id not in vip_users and not await is_admin(message.from_user.id):
        return await message.reply("⛔ VIP command only!")
    
    try:
        _, uid = message.text.split()
    except ValueError:
        return await message.reply("Usage: /visits <uid>")
    
    if not re.fullmatch(r"\d{6,15}", uid):
        return await message.reply("Invalid UID format (6-15 digits)")
    
    temp_msg = await message.reply("🔄 Sending VIP visits (10k)...")
    
    try:
        success = 0
        tokens = 0
        async with httpx.AsyncClient(timeout=60.0) as client:
            for _ in range(10):  # 10 x 1000 = 10k
                response = await client.get(f"{VISIT_API_URL}{uid}")
                data = response.json()
                if "Successfully Sent 1000 visits" in str(data):
                    success += 1
                    if match := re.search(r"Token Count: (\d+)", str(data)):
                        tokens = match.group(1)
        
        result = (
            f"🎖️ {success * 1000} VIP Visits Sent\n"
            f"UID: {uid}\n"
            f"Tokens Left: {tokens}"
        ) if success > 0 else "❌ Failed to send visits"
        
        await delete_message_with_delay(message.chat.id, temp_msg.message_id)
        await message.reply(result)
        
    except Exception as e:
        logger.error(f"VIP visits error: {e}")
        await message.reply("❌ Error sending VIP visits")

@dp.message(Command("allowvisit"))
async def allow_visit_command(message: types.Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admin command only!")
    
    try:
        _, user_id = message.text.split()
        user_id = int(user_id)
        vip_users.add(user_id)
        await message.reply(f"✅ User {user_id} added to VIP list")
    except (ValueError, IndexError):
        await message.reply("Usage: /allowvisit <user_id>")

@dp.message(Command("baninfo"))
async def ban_info_command(message: types.Message):
    if message.chat.id not in ALLOWED_CHAT_IDS:
        return await message.reply("❌ This bot works only in specific groups!")
    
    try:
        _, uid = message.text.split()
    except ValueError:
        return await message.reply("Usage: /baninfo <uid>")
    
    if not re.fullmatch(r"\d{6,15}", uid):
        return await message.reply("Invalid UID format (6-15 digits)")
    
    temp_msg = await message.reply("🔄 Checking ban status...")
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(f"{BAN_INFO_URL}{uid}")
            data = response.json()
            
            if "ban_status" in data:
                if "not banned" in data["ban_status"].lower():
                    result = "✅ Account not banned"
                else:
                    result = f"⛔ {data['ban_status']}"
            else:
                result = "❌ Could not determine ban status"
        
        await delete_message_with_delay(message.chat.id, temp_msg.message_id)
        await message.reply(result)
        
    except Exception as e:
        logger.error(f"Ban check error: {e}")
        await message.reply("❌ Error checking ban status")

@dp.message(Command("setapi"))
async def set_api_command(message: types.Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admin command only!")
    
    try:
        _, api_num = message.text.split()
        api_num = int(api_num)
        if api_num in (1, 2):
            global current_api
            current_api = api_num
            await message.reply(f"✅ Switched to API {api_num}")
        else:
            await message.reply("Usage: /setapi <1|2>")
    except (ValueError, IndexError):
        await message.reply("Usage: /setapi <1|2>")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
