import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InputTextMessageContent, InlineQueryResultArticle

API_ID = "26661233"
API_HASH = "2714c0f32cbede4c64f4e9fd628dbe29"
BOT_TOKEN = "6279192368:AAE3nKbs_ViYJYZ2CCnE3PpX7Q5GDcbJvGo"

# Bot client
bot = Client(
    "string_session_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

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
    instructions = (
        "Please send me your **Phone Number** in international format (e.g., +1234567890) "
        "so I can send you the login code to generate your session."
    )
    await message.reply_text(instructions)
    
    phone_number_msg = await bot.listen(message.chat.id)
    phone_number = phone_number_msg.text

    async with Client("my_account", api_id=API_ID, api_hash=API_HASH) as app:
        try:
            await app.send_code(phone_number)

            await message.reply_text("Please enter the **login code** you received.")

            login_code_msg = await bot.listen(message.chat.id)
            login_code = login_code_msg.text

            await app.sign_in(phone_number, login_code)

            if await app.check_password():
                await message.reply_text("Please enter your **2FA password**.")
                
                password_msg = await bot.listen(message.chat.id)
                password = password_msg.text
                
                await app.check_password(password)

            string_session = app.export_session_string()
            string_message = (
                f"**Pyrogram String Session**:\n\n"
                f"`{string_session}`\n\n"
                "⚠️ *Keep it safe and do not share it with anyone.*"
            )

            await message.reply_text(string_message)

            # Send a copy to the user's saved messages
            await app.send_message("me", string_message)

            # Confirm the string session was saved to the user's messages
            await message.reply_text("Your string session has been saved to your Saved Messages.")

        except Exception as e:
            await message.reply_text(f"An error occurred: `{str(e)}`\nPlease try again.")

@bot.on_inline_query(filters.regex(r''))
async def inline_query_handler(client: Client, query):
    results = [
        InlineQueryResultArticle(
            title="Generate String Session",
            description="Start the process to generate a Pyrogram string session",
            input_message_content=InputTextMessageContent("/generate"),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Start Generating", switch_inline_query_current_chat="/generate")]]
            )
        ),
    ]
    await query.answer(results, cache_time=1)

if __name__ == "__main__":
    bot.run()
