import logging
import os
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded
from pyrogram.types import Message

# Configure logging
logging.basicConfig(level=logging.INFO)

API_ID = "26661233"  # Replace with your API_ID
API_HASH = "2714c0f32cbede4c64f4e9fd628dbe29"  # Replace with your API_HASH
BOT_TOKEN = "6279192368:AAE3nKbs_ViYJYZ2CCnE3PpX7Q5GDcbJvGo"  # Replace with your BOT_TOKEN

bot = Client(
    "string_session_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Store user state
user_state = {}

@bot.on_message(filters.private & filters.command("start"))
async def start(client: Client, message: Message):
    welcome_text = (
        "👋 Welcome to the Pyrogram String Session Generator Bot!\n\n"
        "I can help you generate your Pyrogram string session.\n\n"
        "To get started, use /generate command."
    )
    await message.reply_text(welcome_text)

@bot.on_message(filters.private & filters.command("generate"))
async def generate_string_session(client: Client, message: Message):
    user_id = message.from_user.id
    instructions = (
        "Please send me your **Phone Number** in international format (e.g., +1234567890) "
        "so I can send you the login code to generate your session."
    )
    user_state[user_id] = {"step": "phone_number"}
    await message.reply_text(instructions)

@bot.on_message(filters.private)
async def handle_response(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_state:
        state = user_state[user_id]
        
        if state["step"] == "phone_number":
            phone_number = message.text
            user_state[user_id]["step"] = "login_code"
            
            try:
                async with Client("my_account", api_id=API_ID, api_hash=API_HASH) as app:
                    await app.send_code(phone_number)
                    await message.reply_text("Please enter the **login code** you received.")
            except Exception as e:
                await message.reply_text(f"An error occurred: `{str(e)}`\nPlease try again.")
                del user_state[user_id]

        elif state["step"] == "login_code":
            login_code = message.text
            user_state[user_id]["step"] = "2fa_password"
            
            try:
                async with Client("my_account", api_id=API_ID, api_hash=API_HASH) as app:
                    await app.sign_in(phone_number, login_code)
                    if await app.check_password():
                        await message.reply_text("Please enter your **2FA password**.")
                    else:
                        string_session = app.export_session_string()
                        string_message = (
                            f"**Pyrogram String Session**:\n\n"
                            f"`{string_session}`\n\n"
                            "⚠️ *Keep it safe and do not share it with anyone.*"
                        )
                        await message.reply_text(string_message)
                        await app.send_message("me", string_message)
                        await message.reply_text("Your string session has been saved to your Saved Messages.")
                    
            except SessionPasswordNeeded:
                await message.reply_text("This account has 2FA enabled. Please enter your password.")
            except Exception as e:
                await message.reply_text(f"An error occurred: `{str(e)}`\nPlease try again.")
                del user_state[user_id]

        elif state["step"] == "2fa_password":
            password = message.text
            try:
                async with Client("my_account", api_id=API_ID, api_hash=API_HASH) as app:
                    await app.check_password(password)
                    string_session = app.export_session_string()
                    string_message = (
                        f"**Pyrogram String Session**:\n\n"
                        f"`{string_session}`\n\n"
                        "⚠️ *Keep it safe and do not share it with anyone.*"
                    )
                    await message.reply_text(string_message)
                    await app.send_message("me", string_message)
                    await message.reply_text("Your string session has been saved to your Saved Messages.")
                    
            except Exception as e:
                await message.reply_text(f"An error occurred: `{str(e)}`\nPlease try again.")
                del user_state[user_id]

        else:
            await message.reply_text("Please use /generate to start the session generation process.")

if __name__ == "__main__":
    bot.run()
