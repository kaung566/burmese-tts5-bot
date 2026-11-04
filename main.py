import os
import uuid
import edge_tts
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 32971636))          # မိမိ Telegram API ID
API_HASH = os.environ.get("API_HASH", "54178f4e37ec82caaa218ff1a2d8e8c0")    # မိမိ Telegram API Hash
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9283733881:AAFInOE6EZoB6Ypb7WppgT8lFfkmqMBUolU") # FadeHost မှ အလိုအလျောက် ယူပါမည်

# Force Join Channels (@ ထည့်သွင်းထားပါသည်)
FORCE_CHANNELS = ["@movierecaps6", "@movierecaps67"]

app = Client(
    "burmese_tts_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    workers=30
)

# User တစ်ဦးချင်းစီ၏ Voice, Speed, Pitch မှတ်သားရန်
user_settings = {}

# အသံ ၁၄ မျိုး သတ်မှတ်ချက်များ
VOICES = {
    "v1":  {"name": "မောင်ကောင်း",   "voice": "my-MM-ThihaNeural",                 "gender": "male",   "rate": "+18%", "pitch": "+0Hz"},
    "v2":  {"name": "မယ်ဖွား",      "voice": "my-MM-NilarNeural",                 "gender": "female", "rate": "+18%", "pitch": "+0Hz"},
    "v3":  {"name": "မောင်ရွှေဦး",   "voice": "it-IT-GiuseppeMultilingualNeural",  "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v4":  {"name": "မောင်သာအောင်", "voice": "en-AU-WilliamMultilingualNeural",   "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v5":  {"name": "ဘိုထွန်း",     "voice": "en-US-AndrewMultilingualNeural",    "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v6":  {"name": "မယ်သီရိ",     "voice": "en-US-AvaMultilingualNeural",       "gender": "female", "rate": "+15%", "pitch": "+0Hz"},
    "v7":  {"name": "ဘအောင်",      "voice": "en-US-BrianMultilingualNeural",     "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v8":  {"name": "မြသီ",        "voice": "en-US-EmmaMultilingualNeural",      "gender": "female", "rate": "+15%", "pitch": "+0Hz"},
    "v9":  {"name": "ဘဦး",         "voice": "fr-FR-RemyMultilingualNeural",      "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v10": {"name": "မယ်နွဲ့",      "voice": "fr-FR-VivienneMultilingualNeural",  "gender": "female", "rate": "+15%", "pitch": "+0Hz"},
    "v11": {"name": "မယ်စိန်",      "voice": "de-DE-SeraphinaMultilingualNeural", "gender": "female", "rate": "+15%", "pitch": "+0Hz"},
    "v12": {"name": "ဦးတောင်",      "voice": "de-DE-FlorianMultilingualNeural",   "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v13": {"name": "မယ်နန်း",      "voice": "pt-BR-ThalitaMultilingualNeural",   "gender": "female", "rate": "+15%", "pitch": "+0Hz"},
    "v14": {"name": "ကျော်စွာ",     "voice": "ko-KR-HyunsuMultilingualNeural",    "gender": "male",   "rate": "+15%", "pitch": "+0Hz"}
}

# Speed Presets
SPEED_PRESETS = {
    "default": "မူလအသံနှုန်း",
    "-10%": "🐌 နှေး (-10%)",
    "+0%": "🚶 ပုံမှန် (0%)",
    "+15%": "🏃 အမြန် (+15%)",
    "+25%": "🚀 ပိုမြန် (+25%)",
    "+35%": "⚡ အလွန်မြန် (+35%)"
}

# Pitch Presets
PITCH_PRESETS = {
    "default": "မူလအသံအနိမ့်အမြင့်",
    "-15Hz": "🔉 အသံအလွန်နက် (-15Hz)",
    "-8Hz": "🔉 အသံနက် (-8Hz)",
    "+0Hz": "🎙️ ပုံမှန် (+0Hz)",
    "+8Hz": "🔊 အသံစူး (+8Hz)",
    "+15Hz": "🔊 အသံအလွန်စူး (+15Hz)"
}

WELCOME_TEXT = (
    "🙏 Burmese Text to speech tg bot မှ ကြိုဆိုပါတယ် 🙏\n\n"
    "အသံထုတ်ရတာအဆင်မပြေပါက Admin - @r4nzzyy (သို့)မဟုတ်Gpထဲတွင်တိုက်ရိုက်မေးလို့ရပါသည်😉\n"
    "အသုံးပြုသူများ အားလုံး စိတ်ချမ်းသာ ကိုယ်ကျန်းမာစွာဖြင့် အဆင်ပြေကြပါစေခင်ဗျာ✨\n\n"
    "👇 အသံပုံစံ ကို ရွေးချယ်ပေးပါ-"
)

def get_user_conf(user_id):
    if user_id not in user_settings:
        user_settings[user_id] = {
            "voice": "v1",
            "speed": "default",
            "pitch": "default"
        }
    return user_settings[user_id]

async def is_user_subscribed(client: Client, user_id: int):
    for ch in FORCE_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status not in [
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.RESTRICTED
            ]:
                return False
        except Exception:
            return False
    return True

def get_fsub_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Channel 1 သို့ Join ရန်", url="https://t.me/movierecaps6")],
        [InlineKeyboardButton("📢 Channel 2 သို့ Join ရန်", url="https://t.me/movierecaps67")],
        [InlineKeyboardButton("🔄 စစ်ဆေးမည် (Verify)", callback_data="check_fsub")]
    ])

def build_voice_keyboard(user_id):
    conf = get_user_conf(user_id)
    selected_v = conf["voice"]
    buttons = []
    keys = list(VOICES.keys())

    for i in range(0, len(keys), 2):
        row = []
        k1 = keys[i]
        icon1 = "✅ " if k1 == selected_v else "🎙️ "
        row.append(InlineKeyboardButton(f"{icon1}{VOICES[k1]['name']}", callback_data=f"setv|{k1}"))

        if i + 1 < len(keys):
            k2 = keys[i+1]
            icon2 = "✅ " if k2 == selected_v else "🎙️ "
            row.append(InlineKeyboardButton(f"{icon2}{VOICES[k2]['name']}", callback_data=f"setv|{k2}"))
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton("🔊 လက်ရှိရွေးထားသော အသံကို စမ်းနားထောင်ရန်", callback_data="preview_voice")
    ])

    buttons.append([
        InlineKeyboardButton(f"⚡ Speed: {conf['speed']}", callback_data="menu_speed"),
        InlineKeyboardButton(f"🎚️ Pitch: {conf['pitch']}", callback_data="menu_pitch")
    ])
    return InlineKeyboardMarkup(buttons)

def build_speed_keyboard(user_id):
    conf = get_user_conf(user_id)
    buttons = []
    row = []
    for spd_key, spd_name in SPEED_PRESETS.items():
        icon = "✅ " if conf["speed"] == spd_key else ""
        row.append(InlineKeyboardButton(f"{icon}{spd_name}", callback_data=f"set_spd|{spd_key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("⬅️ ပင်မအသံရွေးချယ်မှုသို့ ပြန်သွားရန်", callback_data="menu_main")])
    return InlineKeyboardMarkup(buttons)

def build_pitch_keyboard(user_id):
    conf = get_user_conf(user_id)
    buttons = []
    row = []
    for ptc_key, ptc_name in PITCH_PRESETS.items():
        icon = "✅ " if conf["pitch"] == ptc_key else ""
        row.append(InlineKeyboardButton(f"{icon}{ptc_name}", callback_data=f"set_ptc|{ptc_key}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("⬅️ ပင်မအသံရွေးချယ်မှုသို့ ပြန်သွားရန်", callback_data="menu_main")])
    return InlineKeyboardMarkup(buttons)

# --- 1. /START COMMAND ---
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    user_id = message.from_user.id
    print(f"📩 /start command received from: {user_id}")
    if not await is_user_subscribed(client, user_id):
        return await message.reply(
            "⚠️ **Bot ကို အသုံးမပြုမီ အောက်ပါ Channel (၂) ခုလုံးကို မဖြစ်မနေ Join ပေးရပါမည် -**",
            reply_markup=get_fsub_keyboard()
        )
    await message.reply(WELCOME_TEXT, reply_markup=build_voice_keyboard(user_id))

# --- 2. CALLBACK QUERY HANDLERS ---
@app.on_callback_query()
async def handle_callback(client, cq: CallbackQuery):
    user_id = cq.from_user.id
    data = cq.data
    conf = get_user_conf(user_id)

    if data == "check_fsub":
        if await is_user_subscribed(client, user_id):
            await cq.message.delete()
            return await cq.message.reply(WELCOME_TEXT, reply_markup=build_voice_keyboard(user_id))
        else:
            return await cq.answer("❌ Channel ၂ ခုလုံးကို မ Join ရသေးပါ။ အရင် Join ပေးပါ။", show_alert=True)

    elif data == "menu_main":
        await cq.message.edit_text(WELCOME_TEXT, reply_markup=build_voice_keyboard(user_id))

    elif data == "menu_speed":
        await cq.message.edit_text(
            f"⚡ **အသံထွက်နှုန်း (Speed / Rate) ချိန်ညှိရန် -**\n"
            f"လက်ရှိရွေးထားသောနှုန်း: `{conf['speed']}`\n\n"
            f"စိတ်ကြိုက် Preset တစ်ခု ရွေးချယ်ပါ:",
            reply_markup=build_speed_keyboard(user_id)
        )

    elif data == "menu_pitch":
        await cq.message.edit_text(
            f"🎚️ **အသံအနိမ့်အမြင့် (Pitch) ချိန်ညှိရန် -**\n"
            f"လက်ရှိရွေးထားသောအဆင့်: `{conf['pitch']}`\n\n"
            f"စိတ်ကြိုက် Preset တစ်ခု ရွေးချယ်ပါ:",
            reply_markup=build_pitch_keyboard(user_id)
        )

    elif data.startswith("set_spd|"):
        spd = data.split("|")[1]
        conf["speed"] = spd
        await cq.message.edit_reply_markup(reply_markup=build_speed_keyboard(user_id))
        await cq.answer(f"Speed ကို {spd} သို့ ပြောင်းလိုက်ပါပြီ။")

    elif data.startswith("set_ptc|"):
        ptc = data.split("|")[1]
        conf["pitch"] = ptc
        await cq.message.edit_reply_markup(reply_markup=build_pitch_keyboard(user_id))
        await cq.answer(f"Pitch ကို {ptc} သို့ ပြောင်းလိုက်ပါပြီ။")

    elif data.startswith("setv|"):
        v_key = data.split("|")[1]
        conf["voice"] = v_key
        await cq.message.edit_reply_markup(reply_markup=build_voice_keyboard(user_id))
        await cq.answer(f"အသံကို {VOICES[v_key]['name']} သို့ ပြောင်းလိုက်ပါပြီ။")

    elif data == "preview_voice":
        v_key = conf["voice"]
        v_data = VOICES[v_key]

        rate = v_data["rate"] if conf["speed"] == "default" else conf["speed"]
        pitch = v_data["pitch"] if conf["pitch"] == "default" else conf["pitch"]

        sample_text = f"မင်္ဂလာပါ။ ကျွန်တော် ကျွန်မကတော့ {v_data['name']} ဖြစ်ပါတယ်။ အသံစမ်းသပ်ခြင်း ဖြစ်ပါတယ်။"
        sample_file = f"sample_{user_id}_{uuid.uuid4().hex[:6]}.mp3"
        await cq.answer("အသံနမူနာ ဖန်တီးနေပါသည်...")

        try:
            comm = edge_tts.Communicate(sample_text, v_data["voice"], rate=rate, pitch=pitch)
            await comm.save(sample_file)
            await client.send_audio(
                chat_id=cq.message.chat.id,
                audio=sample_file,
                title=f"Sample: {v_data['name']}",
                caption=f"🔊 **စမ်းသပ်သံ:** `{v_data['name']}`\n⚡ Speed: `{rate}` | 🎚️ Pitch: `{pitch}`"
            )
        except Exception as e:
            await cq.message.reply(f"❌ အမှားဖြစ်ပွားပါသည်: {str(e)}")
        finally:
            if os.path.exists(sample_file):
                os.remove(sample_file)

# --- 3. TEXT-TO-SPEECH (အပြိုင် ထုတ်လုပ်နိုင်သော စနစ်) ---
@app.on_message(filters.text & ~filters.command(["start"]))
async def tts_handler(client, message):
    user_id = message.from_user.id
    if not await is_user_subscribed(client, user_id):
        return await message.reply(
            "⚠️ **Bot ကို အသုံးမပြုမီ အောက်ပါ Channel (၂) ခုလုံးကို အရင် Join ပေးပါ -**",
            reply_markup=get_fsub_keyboard()
        )

    text = message.text.strip()

    if len(text) > 3000:
        return await message.reply(
            f"⚠️ **စာလုံးရေ ကန့်သတ်ချက် ကျော်လွန်နေပါသည်!**\n"
            f"လက်ရှိ စာလုံးရေ: `{len(text)}` လုံး\n"
            f"အများဆုံး စာလုံးရေ `၃၀၀၀` အထိသာ လက်ခံနိုင်ပါသည်။"
        )

    conf = get_user_conf(user_id)
    v_key = conf["voice"]
    v_data = VOICES[v_key]

    rate = v_data["rate"] if conf["speed"] == "default" else conf["speed"]
    pitch = v_data["pitch"] if conf["pitch"] == "default" else conf["pitch"]

    status_msg = await message.reply("⏳ **အသံပြောင်းလဲနေပါသည်... ခေတ္တစောင့်ပေးပါ...**")
    out_file = f"tts_{user_id}_{message.id}_{uuid.uuid4().hex[:6]}.mp3"

    try:
        communicate = edge_tts.Communicate(text, v_data["voice"], rate=rate, pitch=pitch)
        await communicate.save(out_file)

        caption_text = (
            f"🗣️ **အသံ:** `{v_data['name']}`\n"
            f"⚡ Speed: `{rate}` | 🎚️ Pitch: `{pitch}`\n"
            f"📝 စာလုံးရေ: `{len(text)}` လုံး"
        )

        await client.send_audio(
            chat_id=message.chat.id,
            audio=out_file,
            title=f"TTS - {v_data['name']}",
            caption=caption_text
        )
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ အသံထုတ်ရာတွင် Error ဖြစ်ပွားပါသည်: `{str(e)}`")

    finally:
        if os.path.exists(out_file):
            os.remove(out_file)

# --- RUN BOT ---
if __name__ == "__main__":
    print("✅ 14-Voice Burmese TTS Bot is online with app.run()!")
    app.run()
