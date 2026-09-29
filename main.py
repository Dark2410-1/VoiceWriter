import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from asyncio import run

from ovozlar import generate_speech, VOICES

TOKEN = os.getenv("BOT_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(TOKEN)
dp = Dispatcher()

# Store user voice preferences: {user_id: "sardor" / "madina"}
user_voices = {}

def get_voice_keyboard(current_voice: str = "sardor"):
    keyboard = []
    for key, info in VOICES.items():
        prefix = "✅ " if key == current_voice else ""
        keyboard.append([
            InlineKeyboardButton(text=f"{prefix}{info['title']}", callback_data=f"voice_{key}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(Command("start"))
async def start_cmd(message: Message):
    user_id = message.from_user.id
    if user_id not in user_voices:
        user_voices[user_id] = "sardor"
        
    current_voice = user_voices[user_id]
    voice_title = VOICES[current_voice]['title']
    
    text = (
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>! 👋\n\n"
        f"Men matnni tabiiy ovozga aylantirib beruvchi professional botman (Text-to-Speech).\n\n"
        f"📝 Menga istalgan matnni yuboring, men uni ovozli xabarga aylantirib beraman.\n"
        f"⚙️ Hozirgi ovoz: <b>{voice_title}</b>\n\n"
        f"Ovozni o'zgartirish uchun /settings buyrug'idan foydalaning."
    )
    await message.answer(text, parse_mode="HTML", reply_markup=get_voice_keyboard(current_voice))

@dp.message(Command("help"))
async def help_cmd(message: Message):
    text = (
        "📖 <b>Botdan foydalanish yo'riqnomasi:</b>\n\n"
        "1. Menga xohlagan o'zbekcha (yoki boshqa tildagi) matningizni yuboring.\n"
        "2. Bot matnni ovozli xabar ko'rinishida yuboradi.\n"
        "3. /settings buyrug'i orqali erkak yoki ayol ovozini tanlashingiz mumkin.\n\n"
        "Savollar bo'yicha: @username"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("settings"))
async def settings_cmd(message: Message):
    user_id = message.from_user.id
    current_voice = user_voices.get(user_id, "sardor")
    await message.answer(
        "🎙 <b>Ovoz turini tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_voice_keyboard(current_voice)
    )

@dp.callback_query(F.data.startswith("voice_"))
async def voice_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    voice_key = callback.data.split("_")[1]
    
    if voice_key in VOICES:
        user_voices[user_id] = voice_key
        voice_title = VOICES[voice_key]['title']
        await callback.message.edit_text(
            f"✅ Ovoz muvaffaqiyatli o'zgartirildi!\n\nJoriy ovoz: <b>{voice_title}</b>\n\nEndi matn yuborishingiz mumkin.",
            parse_mode="HTML",
            reply_markup=get_voice_keyboard(voice_key)
        )
        await callback.answer("Ovoz saqlandi!")
    else:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)

@dp.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if not text:
        return

    if len(text) > 4000:
        await message.answer("⚠️ Matn juda uzun! Iltimos, 4000 ta belgidan kamroq matn yuboring.")
        return

    current_voice = user_voices.get(user_id, "sardor")
    
    # Send typing/recording action
    await bot.send_chat_action(chat_id=message.chat.id, action="record_voice")
    
    output_file = None
    try:
        output_file = await generate_speech(text, current_voice)
        audio_file = FSInputFile(output_file)
        
        await message.answer_voice(
            voice=audio_file,
            caption=f"🎧 Matn ovozga aylantirildi ({VOICES[current_voice]['title']})"
        )
    except Exception as e:
        logging.error(f"TTS Error: {e}")
        await message.answer("❌ Ovozni yaratishda xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
    finally:
        # Cleanup temp file
        if output_file and os.path.exists(output_file):
            try:
                os.remove(output_file)
            except Exception:
                pass

async def main():
    logging.info("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    run(main())
