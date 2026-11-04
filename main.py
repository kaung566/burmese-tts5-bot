import os
import uuid
import edge_tts
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 2040))
API_HASH = os.environ.get("API_HASH", "b18441a1ff607e10a989891a5462e627")
BOT_TOKEN = (
    os.environ.get("BOT_TOKEN")
    or os.environ.get("TELEGRAM_BOT_TOKEN")
    or os.environ.get("TOKEN")
    or "YOUR_BOT_TOKEN"
)

# Force Join Channels
FORCE_CHANNELS = ["@movierecaps6", "@movierecaps67"]

app = Client(
    "burmese_tts_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    workers=30
)

# User တစ်ဦးချင်းစီ၏ ရွေးချယ်မှုနှင့် စာသား မှတ်သားရန်
user_settings = {}
user_last_text = {}

# မြန်မာစာ ၁၀၀% အလုပ်လုပ်သော အသံ ၁၄ မျိုး
VOICES = {
    "v1":  {"name": "မောင်ကောက်",   "voice": "my-MM-ThihaNeural", "gender": "male",   "rate": "+18%", "pitch": "+0Hz"},
    "v2":  {"name": "မယ်ဖွား",      "voice": "my-MM-NilarNeural", "gender": "female", "rate": "+18%", "pitch": "+0Hz"},
    "v3":  {"name": "မောင်ရွှေဦး",   "voice": "my-MM-ThihaNeural", "gender": "male",   "rate": "+10%", "pitch": "-8Hz"},
    "v4":  {"name": "မောင်သာအောင်", "voice": "my-MM-ThihaNeural", "gender": "male",   "rate": "+24%", "pitch": "+10Hz"},
    "v5":  {"name": "ဘိုထွန်း",     "voice": "my-MM-ThihaNeural", "gender": "male",   "rate": "+4%",  "pitch": "-16Hz"},
    "v6":  {"name": "မယ်သီရိ",     "voice": "my-MM-NilarNeural", "gender": "female", "rate": "+20%", "pitch": "+12Hz"},
    "v7":  {"name": "ဘအောင်",      "voice": "my-MM-ThihaNeural", "gender": "male",   "rate": "+12%", "pitch": "-5Hz"},
    "v8":  {"name": "မြသီ",        "voice": "my-MM-NilarNeural", "gender": "female", "rate": "+8%",  "pitch": "-6Hz"},
    "v9":  {"name": "ဘဦး",         "voice": "my-MM-ThihaNeural", "gender": "male",   "rate": "+16%", "pitch": "+6Hz"},
    "v10": {"name": "မယ်နွဲ့",      "voice": "my-MM-NilarNeural", "gender": "female", "rate": "+16%", "pitch": "+6Hz"},
    "v11": {"name": "မယ်စိန်",      "voice": "my-MM-NilarNeural", "gender": "female", "rate": "+6%",  "pitch": "-12Hz"},
    "v12": {"name": "ဦးတောင်",      "voice": "my-MM-ThihaNeural", "gender": "male",   "rate": "+8%",  "pitch": "-14Hz"},
    "v13": {"name": "မယ်နန်း",      "voice": "my-MM-NilarNeural", "gender": "female", "rate": "+22%", "pitch": "+16Hz"},
    "v14": {"name": "ကျော်စွာ",     "voice": "my-MM-ThihaNeural", "gender": "male",   "rate": "+24%", "pitch": "+12Hz"}
}

# Speed Presets (အသံနှုန်း)
SPEED_PRESETS = {
    "-10%": "🐌 နှေး",
    "+0%": "🚶 ပုံမှန်",
    "default": "⚡ မူလ",
    "+25%": "🏃 မြန်",
    "+35%": "🚀 အမြန်"
}

# Pitch Presets (အသံအနိမ့်အမြင့်)
PITCH_PRESETS = {
    "-12Hz": "🔉 အသံဩ",
    "-6Hz": "🔉 အသံနက်",
    "default": "🎙️ မူလ",
    "+6Hz": "🔊 အသံမြင့်",
    "+12Hz": "🔊 အသံစူး"
}

WELCOME_TEXT = (
    "🙏 Burmese Text to speech tg bot မှ ကြိုဆိုပါတယ် 🙏\n"
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

def resolve_rate_pitch(conf):
    v_data = VOICES[conf["voice"]]
    rate = v_data["rate"] if conf["speed"] == "default" else conf["speed"]
    pitch = v_data["pitch"] if conf["pitch"] == "default" else conf["pitch"]
    return v_data, rate, pitch

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
        except UserNotParticipant:
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

def build_start_keyboard(user_id):
    """/start နှိပ်သည့်အခါ ပြသမည့် အသံ ၁၄ မျိုးနှင့် စမ်းသပ်သံ ခလုတ်"""
    conf = get_user_conf(user_id)
    selected_v = conf["voice"]
    buttons = []
    keys = list(VOICES.keys())

    for i in range(0, len(keys), 2):
        row = []
        k1 = keys[i]
        icon1 = "✅ " if k1 == selected_v else "🎙️ "
        row.append(InlineKeyboardButton(f"{icon1}{VOICES[k1]['name']}", callback_data=f"startv|{k1}"))

        if i + 1 < len(keys):
            k2 = keys[i + 1]
            icon2 = "✅ " if k2 == selected_v else "🎙️ "
            row.append(InlineKeyboardButton(f"{icon2}{VOICES[k2]['name']}", callback_data=f"startv|{k2}"))
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton("🔊 လက်ရှိရွေးထားသော အသံကို စမ်းနားထောင်ရန်", callback_data="preview_voice")
    ])
    return InlineKeyboardMarkup(buttons)

def build_panel_text(user_id, text_len):
    conf = get_user_conf(user_id)
    v_data, rate, pitch = resolve_rate_pitch(conf)
    return (
        f"📝 **စာလုံးရေ:** `{text_len}` / 3000 လုံး\n"
        f"🗣️ **လက်ရှိအသံ:** `{v_data['name']}`\n"
        f"⚡ **Speed:** `{rate}` | 🎚️ **Pitch:** `{pitch}`\n\n"
        f"👇 အသံ၊ Speed နှင့် Pitch တို့ကို စိတ်ကြိုက်ရွေးချယ်ပြီး **အသံထုတ်မည်** ကို နှိပ်ပါ-"
    )

def build_tts_panel_keyboard(user_id):
    """စာသားပို့ပြီးသည့်အခါ အသံ ၁၄ မျိုး + Speed + Pitch + အသံထုတ်မည် ခလုတ်များ ပေါင်းစပ်ထားသော ကီးဘုတ်"""
    conf = get_user_conf(user_id)
    selected_v = conf["voice"]
    buttons = []
    keys = list(VOICES.keys())

    # ၁။ အသံ ၁၄ မျိုး ရွေးချယ်ရန်
    for i in range(0, len(keys), 2):
        row = []
        k1 = keys[i]
        icon1 = "✅ " if k1 == selected_v else "🎙️ "
        row.append(InlineKeyboardButton(f"{icon1}{VOICES[k1]['name']}", callback_data=f"panelv|{k1}"))

        if i + 1 < len(keys):
            k2 = keys[i + 1]
            icon2 = "✅ " if k2 == selected_v else "🎙️ "
            row.append(InlineKeyboardButton(f"{icon2}{VOICES[k2]['name']}", callback_data=f"panelv|{k2}"))
        buttons.append(row)

    # ၂။ Speed (အသံနှုန်း) ချိန်ညှိရန် ခလုတ်တန်း
    spd_row = []
    for spd_key, spd_label in SPEED_PRESETS.items():
        mark = "✅" if conf["speed"] == spd_key else ""
        spd_row.append(InlineKeyboardButton(f"{mark}{spd_label}", callback_data=f"spd|{spd_key}"))
    buttons.append(spd_row)

    # ၃။ Pitch (အသံအနိမ့်အမြင့်) ချိန်ညှိရန် ခလုတ်တန်း
    ptc_row = []
    for ptc_key, ptc_label in PITCH_PRESETS.items():
        mark = "✅" if conf["pitch"] == ptc_key else ""
        ptc_row.append(InlineKeyboardButton(f"{mark}{ptc_label}", callback_data=f"ptc|{ptc_key}"))
    buttons.append(ptc_row)

    # ၄။ အသံစမ်းနားထောင်ရန် နှင့် အသံထုတ်မည် ခလုတ်
    buttons.append([
        InlineKeyboardButton("🔊 အသံစမ်းနားထောင်ရန်", callback_data="preview_voice")
    ])
    buttons.append([
        InlineKeyboardButton("🚀 အသံထုတ်မည် (Generate Audio)", callback_data="generate_tts")
    ])

    return InlineKeyboardMarkup(buttons)

# --- 1. /START COMMAND ---
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    user_id = message.from_user.id
    if not await is_user_subscribed(client, user_id):
        return await message.reply(
            "⚠️ **Bot ကို အသုံးမပြုမီ အောက်ပါ Channel (၂) ခုလုံးကို မဖြစ်မနေ Join ပေးရပါမည် -**",
            reply_markup=get_fsub_keyboard()
        )
    await message.reply(WELCOME_TEXT, reply_markup=build_start_keyboard(user_id))

# --- 2. TEXT HANDLER (စာပို့လိုက်သည့်အခါ ရွေးချယ်စရာ Panel ပြပေးခြင်း) ---
@app.on_message(filters.text & ~filters.command(["start"]))
async def receive_text_handler(client, message):
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

    user_last_text[user_id] = text

    await message.reply(
        build_panel_text(user_id, len(text)),
        reply_markup=build_tts_panel_keyboard(user_id),
        reply_to_message_id=message.id
    )

# --- 3. CALLBACK QUERY HANDLERS ---
@app.on_callback_query()
async def handle_callback(client, cq: CallbackQuery):
    user_id = cq.from_user.id
    data = cq.data
    conf = get_user_conf(user_id)

    # Force-Sub စစ်ဆေးခြင်း
    if data == "check_fsub":
        if await is_user_subscribed(client, user_id):
            await cq.message.delete()
            return await cq.message.reply(WELCOME_TEXT, reply_markup=build_start_keyboard(user_id))
        else:
            return await cq.answer("❌ Channel ၂ ခုလုံးကို မ Join ရသေးပါ။ အရင် Join ပေးပါ။", show_alert=True)

    # /start မီနူးမှ အသံရွေးချယ်ခြင်း
    elif data.startswith("startv|"):
        v_key = data.split("|")[1]
        conf["voice"] = v_key
        await cq.message.edit_reply_markup(reply_markup=build_start_keyboard(user_id))
        await cq.answer(f"အသံကို {VOICES[v_key]['name']} သို့ ပြောင်းလိုက်ပါပြီ။")

    # Text ပို့ပြီးနောက် ပေါ်လာသော Panel မှ အသံ၊ Speed၊ Pitch ပြောင်းလဲခြင်း
    elif data.startswith(("panelv|", "spd|", "ptc|")):
        action, val = data.split("|", 1)
        if action == "panelv":
            conf["voice"] = val
            await cq.answer(f"အသံ: {VOICES[val]['name']}")
        elif action == "spd":
            conf["speed"] = val
            await cq.answer(f"Speed: {SPEED_PRESETS[val]}")
        elif action == "ptc":
            conf["pitch"] = val
            await cq.answer(f"Pitch: {PITCH_PRESETS[val]}")

        orig_text = ""
        if cq.message.reply_to_message and cq.message.reply_to_message.text:
            orig_text = cq.message.reply_to_message.text.strip()
        else:
            orig_text = user_last_text.get(user_id, "")

        await cq.message.edit_text(
            build_panel_text(user_id, len(orig_text)),
            reply_markup=build_tts_panel_keyboard(user_id)
        )

    # အသံနမူနာ စမ်းနားထောင်ခြင်း
    elif data == "preview_voice":
        v_data, rate, pitch = resolve_rate_pitch(conf)
        sample_text = f"မင်္ဂလာပါ။ {v_data['name']} ၏ အသံစမ်းသပ်မှု ဖြစ်ပါတယ်။"
        sample_file = f"sample_{user_id}_{uuid.uuid4().hex[:6]}.mp3"
        await cq.answer("🔊 အသံနမူနာ ထုတ်ပေးနေပါသည်...")

        try:
            comm = edge_tts.Communicate(sample_text, v_data["voice"], rate=rate, pitch=pitch)
            await comm.save(sample_file)
            await client.send_audio(
                chat_id=cq.message.chat.id,
                audio=sample_file,
                title=f"Sample - {v_data['name']}",
                caption=f"🔊 **စမ်းသပ်သံ:** `{v_data['name']}`\n⚡ Speed: `{rate}` | 🎚️ Pitch: `{pitch}`"
            )
        except Exception as e:
            await cq.message.reply(f"❌ စမ်းသပ်သံ ထုတ်ရာတွင် Error ဖြစ်ပွားပါသည်: `{str(e)}`")
        finally:
            if os.path.exists(sample_file):
                os.remove(sample_file)

    # 🚀 အသံထုတ်မည် ခလုတ်နှိပ်သည့်အခါ အပြိုင် (Concurrent) အသံထုတ်ပေးခြင်း
    elif data == "generate_tts":
        if not await is_user_subscribed(client, user_id):
            return await cq.answer("❌ Channel ၂ ခုလုံးကို အရင် Join ပေးပါ။", show_alert=True)

        text = ""
        if cq.message.reply_to_message and cq.message.reply_to_message.text:
            text = cq.message.reply_to_message.text.strip()
        else:
            text = user_last_text.get(user_id, "")

        if not text:
            return await cq.answer("⚠️ အသံထုတ်ရန် စာသား အသစ်ပြန်ပို့ပေးပါ။", show_alert=True)

        if len(text) > 3000:
            return await cq.answer("⚠️ စာလုံးရေ ၃၀၀၀ ထက် ကျော်လွန်နေပါသည်။", show_alert=True)

        v_data, rate, pitch = resolve_rate_pitch(conf)
        await cq.answer("⏳ အသံဖိုင် စတင်ထုတ်လုပ်နေပါပြီ...")

        status_msg = await cq.message.reply("⏳ **အသံပြောင်းလဲနေပါသည်... ခေတ္တစောင့်ပေးပါ...**")
        out_file = f"tts_{user_id}_{uuid.uuid4().hex[:8]}.mp3"

        try:
            communicate = edge_tts.Communicate(text, v_data["voice"], rate=rate, pitch=pitch)
            await communicate.save(out_file)

            caption_text = (
                f"🗣️ **အသံ:** `{v_data['name']}`\n"
                f"⚡ **Speed:** `{rate}` | 🎚️ **Pitch:** `{pitch}`\n"
                f"📝 **စာလုံးရေ:** `{len(text)}` လုံး"
            )

            await client.send_audio(
                chat_id=cq.message.chat.id,
                audio=out_file,
                title=f"{v_data['name']} - Burmese TTS",
                caption=caption_text,
                reply_to_message_id=cq.message.reply_to_message.id if cq.message.reply_to_message else None
            )
            await status_msg.delete()

        except Exception as e:
            await status_msg.edit_text(f"❌ အသံထုတ်ရာတွင် Error ဖြစ်ပွားပါသည်: `{str(e)}`")

        finally:
            if os.path.exists(out_file):
                os.remove(out_file)

# --- RUN BOT ---
if __name__ == "__main__":
    print("✅ 14-Voice Burmese TTS Bot is online!")
    app.run()
