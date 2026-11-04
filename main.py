import os
import re
import uuid
import asyncio
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
CH1 = "movierecaps6"
CH2 = "movierecaps67"

app = Client(
    "burmese_tts_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    workers=30
)

# User တစ်ဦးချင်းစီ၏ Setting နှင့် နောက်ဆုံးပို့ထားသော စာသား မှတ်သားရန်
user_settings = {}
user_last_text = {}

# မူရင်း အသံ ၁၄ မျိုး (Multilingual Neural Voices အပြည့်အစုံ)
VOICES = {
    "v1":  {"name": "🎙️ မောင်ဘကျော်",   "voice": "my-MM-ThihaNeural",                 "gender": "male",   "rate": "+18%", "pitch": "+0Hz"},
    "v2":  {"name": "🎙️ မယ်ဖွား",       "voice": "my-MM-NilarNeural",                 "gender": "female", "rate": "+18%", "pitch": "+0Hz"},
    "v3":  {"name": "🎙️ မောင်ရွှေရိုး",   "voice": "it-IT-GiuseppeMultilingualNeural",  "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v4":  {"name": "🎙️ မောင်သာဒင်",   "voice": "en-AU-WilliamMultilingualNeural",   "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v5":  {"name": "🎙️ ဘိုးထွန်း",     "voice": "en-US-AndrewMultilingualNeural",    "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v6":  {"name": "🎙️ မယ်သိင်္ဂီ",     "voice": "en-US-AvaMultilingualNeural",       "gender": "female", "rate": "+15%", "pitch": "+0Hz"},
    "v7":  {"name": "🎙️ ဘသောင်း",     "voice": "en-US-BrianMultilingualNeural",     "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v8":  {"name": "🎙️ မြသီ",         "voice": "en-US-EmmaMultilingualNeural",      "gender": "female", "rate": "+15%", "pitch": "+0Hz"},
    "v9":  {"name": "🎙️ ဘညွန့်",       "voice": "fr-FR-RemyMultilingualNeural",      "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v10": {"name": "🎙️ မယ်နု",        "voice": "fr-FR-VivienneMultilingualNeural",  "gender": "female", "rate": "+15%", "pitch": "+0Hz"},
    "v11": {"name": "🎙️ မယ်စိန်",      "voice": "de-DE-SeraphinaMultilingualNeural", "gender": "female", "rate": "+15%", "pitch": "+0Hz"},
    "v12": {"name": "🎙️ ဖိုးထောင်",     "voice": "de-DE-FlorianMultilingualNeural",   "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
    "v13": {"name": "🎙️ မယ်နန်း",      "voice": "pt-BR-ThalitaMultilingualNeural",   "gender": "female", "rate": "+15%", "pitch": "+0Hz"},
    "v14": {"name": "🎙️ ကျော်စွာ",      "voice": "ko-KR-HyunsuMultilingualNeural",    "gender": "male",   "rate": "+15%", "pitch": "+0Hz"},
}

# အရောင်စုံ Speed Presets
SPEED_PRESETS = {
    "-10%": "🐢 နှေး",
    "+0%": "🔵 ပုံမှန်",
    "default": "⚡ မူလ",
    "+25%": "🟠 မြန်",
    "+35%": "🔥 အမြန်"
}

# အရောင်စုံ Pitch Presets
PITCH_PRESETS = {
    "-12Hz": "🟣 အသံဩ",
    "-6Hz": "🔵 အသံနက်",
    "default": "🟢 မူလ",
    "+6Hz": "🟡 အသံမြင့်",
    "+12Hz": "🔴 အသံစူး"
}

WELCOME_TEXT = (
    "🙏 Burmese Text to speech tg bot မှ ကြိုဆိုပါတယ် 🙏\n"
    "အသံထုတ်ရတာအဆင်မပြေပါက Admin - @r4nzzyy (သို့)မဟုတ်Gpထဲတွင်တိုက်ရိုက်မေးလို့ရပါသည်😉\n"
    "အသုံးပြုသူများ အားလုံး စိတ်ချမ်းသာ ကိုယ်ကျန်းမာစွာဖြင့် အဆင်ပြေကြပါစေခင်ဗျာ✨\n\n"
    "👇 အသံပုံစံ ကို ရွေးချယ်ပေးပါ-"
)

def clean_voice_name(raw_name: str) -> str:
    return raw_name.replace("🎙️", "").strip()

def get_user_conf(user_id):
    if user_id not in user_settings:
        user_settings[user_id] = {
            "voice": "v1",
            "speed": "default",
            "pitch": "default"
        }
    return user_settings[user_id]

def parse_int_val(val_str: str) -> int:
    try:
        return int(val_str.replace("%", "").replace("Hz", "").replace("+", ""))
    except Exception:
        return 0

def resolve_rate_pitch(conf):
    v_data = VOICES[conf["voice"]]
    rate = v_data["rate"] if conf["speed"] == "default" else conf["speed"]
    pitch = v_data["pitch"] if conf["pitch"] == "default" else conf["pitch"]
    return v_data, rate, pitch

def split_burmese_text(text: str, max_len: int = 350) -> list:
    """စာလုံးရေ ၃၀၀၀ ကို အသံအတက်အကျ ငြိမ်စေရန် ပုဒ်မ (။) အလိုက် အပိုင်းငယ်များ ခွဲထုတ်ခြင်း"""
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[။.!?])\s*', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if not sentence:
            continue
        if len(current_chunk) + len(sentence) + 1 <= max_len:
            current_chunk += (" " + sentence if current_chunk else sentence)
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            if len(sentence) > max_len:
                sub_parts = re.split(r'(?<=[၊,])\s*', sentence)
                sub_chunk = ""
                for part in sub_parts:
                    if len(sub_chunk) + len(part) + 1 <= max_len:
                        sub_chunk += (" " + part if sub_chunk else part)
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk.strip())
                        sub_chunk = part
                current_chunk = sub_chunk
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    # အသံထွက်နိုင်သော စာလုံးပါသည့် အပိုင်းများကိုသာ စစ်ထုတ်ခြင်း
    valid_chunks = [c for c in chunks if re.search(r'[\w\u1000-\u109F]', c)]
    return valid_chunks if valid_chunks else [text]

async def stream_chunks_to_file(chunks: list, voice: str, rate: str, pitch: str, out_file: str):
    """အပိုင်းခွဲထားသော စာသားများကို အသံအတက်အကျ တစ်သမတ်တည်းဖြင့် MP3 တစ်ဖိုင်တည်းသို့ ပေါင်းထည့်ခြင်း"""
    with open(out_file, "wb") as audio_file:
        for chunk in chunks:
            comm = edge_tts.Communicate(
                text=chunk,
                voice=voice,
                rate=rate,
                pitch=pitch,
                volume="+0%"
            )
            async for message in comm.stream():
                if message["type"] == "audio":
                    audio_file.write(message["data"])

async def synthesize_speech(text: str, v_data: dict, rate: str, pitch: str, out_file: str):
    """ရွေးချယ်ထားသော Multilingual Voice ဖြင့် အသံအတက်အကျ ငြိမ်စွာ ထုတ်ပေးသည့် စနစ်"""
    chunks = split_burmese_text(text, max_len=350)
    last_err = None

    # ၁။ ရွေးချယ်ထားသော Voice (ဥပမာ en-US-AndrewMultilingualNeural, ko-KR-HyunsuMultilingualNeural) ဖြင့် တိုက်ရိုက်ထုတ်ယူခြင်း
    for _ in range(2):
        try:
            await stream_chunks_to_file(chunks, v_data["voice"], rate, pitch, out_file)
            if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
                return
        except Exception as e:
            last_err = e
            await asyncio.sleep(0.4)

    # ၂။ Pitch ကြောင့် ငြင်းပယ်ခံရပါက မူလ Pitch (+0Hz) ဖြင့် ထပ်မံစမ်းသပ်ခြင်း
    if pitch != "+0Hz":
        try:
            await stream_chunks_to_file(chunks, v_data["voice"], rate, "+0Hz", out_file)
            if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
                return
        except Exception as e:
            last_err = e

    # ၃။ အကယ်၍ Multilingual Voice က လုံးဝမထွက်သည့် အခြေအနေကြုံမှသာ မြန်မာ Native Voice ဖြင့် အရန်ထုတ်ပေးခြင်း
    fallback_voice = "my-MM-ThihaNeural" if v_data["gender"] == "male" else "my-MM-NilarNeural"
    try:
        await stream_chunks_to_file(chunks, fallback_voice, rate, pitch, out_file)
        if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
            return
    except Exception:
        await stream_chunks_to_file(chunks, fallback_voice, rate, "+0Hz", out_file)
        return

    if last_err:
        raise last_err

async def is_user_subscribed(client: Client, user_id: int):
    for ch in [CH1, CH2]:
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
        except Exception as e:
            print(f"FSub check warning for {ch}: {e}")
            continue
    return True

def get_fsub_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Channel 1 သို့ Join ရန်", url=f"https://t.me/{CH1}")],
        [InlineKeyboardButton("📢 Channel 2 သို့ Join ရန်", url=f"https://t.me/{CH2}")],
        [InlineKeyboardButton("🔄 စစ်ဆေးမည် (Verify)", callback_data="check_fsub")]
    ])

def build_start_keyboard(user_id):
    """/start မီနူးတွင်သာ ပြသမည့် အသံ ၁၄ မျိုး ရွေးချယ်စရာ ကီးဘုတ်"""
    conf = get_user_conf(user_id)
    selected_v = conf["voice"]
    buttons = []
    keys = list(VOICES.keys())

    for i in range(0, len(keys), 2):
        row = []
        k1 = keys[i]
        name1 = clean_voice_name(VOICES[k1]["name"])
        btn_text1 = f"✅ {name1}" if k1 == selected_v else VOICES[k1]["name"]
        row.append(InlineKeyboardButton(btn_text1, callback_data=f"startv|{k1}"))

        if i + 1 < len(keys):
            k2 = keys[i + 1]
            name2 = clean_voice_name(VOICES[k2]["name"])
            btn_text2 = f"✅ {name2}" if k2 == selected_v else VOICES[k2]["name"]
            row.append(InlineKeyboardButton(btn_text2, callback_data=f"startv|{k2}"))
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton("🔊 လက်ရှိရွေးထားသော အသံကို စမ်းနားထောင်ရန်", callback_data="preview_voice")
    ])
    return InlineKeyboardMarkup(buttons)

def build_panel_text(user_id, text_len):
    conf = get_user_conf(user_id)
    v_data, rate, pitch = resolve_rate_pitch(conf)
    v_name = clean_voice_name(v_data["name"])
    return (
        f"📝 **စာလုံးရေ:** `{text_len}` / 3000 လုံး\n"
        f"🗣️ **လက်ရှိအသံ:** `{v_name}`\n"
        f"⚡ **Speed:** `{rate}` | 🌈 **Pitch:** `{pitch}`\n\n"
        f"👇 **Speed** နှင့် **Pitch** ကို စိတ်ကြိုက်ချိန်ညှိပြီး **အသံထုတ်မည်** ကို နှိပ်ပါ-"
    )

def build_tts_panel_keyboard(user_id):
    """စာပို့သည့်အခါ အသံ ၁၄ မျိုး ထပ်မပြတော့ဘဲ Speed/Pitch နှင့် +/- ခလုတ်များကိုသာ အရောင်စုံဖြင့် ပြသမည့် ကီးဘုတ်"""
    conf = get_user_conf(user_id)
    buttons = []

    # ၁။ Speed Presets (အရောင်စုံ ခလုတ်တန်း)
    spd_row = []
    for spd_key, spd_label in SPEED_PRESETS.items():
        mark = "✅" if conf["speed"] == spd_key else ""
        spd_row.append(InlineKeyboardButton(f"{mark}{spd_label}", callback_data=f"spd|{spd_key}"))
    buttons.append(spd_row)

    # ၂။ Speed - / Speed + ချိန်ညှိရန် ခလုတ်တန်း
    buttons.append([
        InlineKeyboardButton("🔽 Speed -5%", callback_data="adj_spd|-5"),
        InlineKeyboardButton("🔼 Speed +5%", callback_data="adj_spd|+5")
    ])

    # ၃။ Pitch Presets (အရောင်စုံ ခလုတ်တန်း)
    ptc_row = []
    for ptc_key, ptc_label in PITCH_PRESETS.items():
        mark = "✅" if conf["pitch"] == ptc_key else ""
        ptc_row.append(InlineKeyboardButton(f"{mark}{ptc_label}", callback_data=f"ptc|{ptc_key}"))
    buttons.append(ptc_row)

    # ၄။ Pitch - / Pitch + ချိန်ညှိရန် ခလုတ်တန်း
    buttons.append([
        InlineKeyboardButton("🔽 Pitch -2Hz", callback_data="adj_ptc|-2"),
        InlineKeyboardButton("🔼 Pitch +2Hz", callback_data="adj_ptc|+2")
    ])

    # ၅။ စမ်းနားထောင်ရန် နှင့် မူလအတိုင်း ပြန်ထားရန်
    buttons.append([
        InlineKeyboardButton("🎧 စမ်းနားထောင်ရန်", callback_data="preview_voice"),
        InlineKeyboardButton("🔄 မူလအတိုင်း", callback_data="reset_sp")
    ])

    # ၆။ အသံထုတ်မည် ခလုတ်
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

# --- 2. TEXT HANDLER (စာပို့လိုက်သည့်အခါ Speed/Pitch Panel ပြပေးခြင်း) ---
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

    # /start မီနူးမှ အသံ ၁၄ မျိုး ရွေးချယ်ခြင်း
    elif data.startswith("startv|"):
        v_key = data.split("|")[1]
        conf["voice"] = v_key
        v_name = clean_voice_name(VOICES[v_key]["name"])
        await cq.message.edit_reply_markup(reply_markup=build_start_keyboard(user_id))
        await cq.answer(f"✅ အသံကို {v_name} သို့ ပြောင်းလိုက်ပါပြီ။")

    # Speed နှင့် Pitch Preset ရွေးချယ်ခြင်း / +/- ချိန်ညှိခြင်း / Reset လုပ်ခြင်း
    elif data.startswith(("spd|", "ptc|", "adj_spd|", "adj_ptc|")) or data == "reset_sp":
        v_data, cur_rate, cur_pitch = resolve_rate_pitch(conf)

        if data == "reset_sp":
            conf["speed"] = "default"
            conf["pitch"] = "default"
            await cq.answer("🔄 မူလ Speed နှင့် Pitch သို့ ပြန်ထားလိုက်ပါပြီ။")

        elif data.startswith("spd|"):
            val = data.split("|", 1)[1]
            conf["speed"] = val
            await cq.answer(f"⚡ Speed: {SPEED_PRESETS[val]}")

        elif data.startswith("ptc|"):
            val = data.split("|", 1)[1]
            conf["pitch"] = val
            await cq.answer(f"🌈 Pitch: {PITCH_PRESETS[val]}")

        elif data.startswith("adj_spd|"):
            delta = int(data.split("|", 1)[1])
            new_spd = max(-50, min(100, parse_int_val(cur_rate) + delta))
            conf["speed"] = f"{new_spd:+d}%"
            await cq.answer(f"⚡ Speed: {conf['speed']}")

        elif data.startswith("adj_ptc|"):
            delta = int(data.split("|", 1)[1])
            new_ptc = max(-30, min(30, parse_int_val(cur_pitch) + delta))
            conf["pitch"] = f"{new_ptc:+d}Hz"
            await cq.answer(f"🌈 Pitch: {conf['pitch']}")

        orig_text = ""
        if cq.message.reply_to_message and cq.message.reply_to_message.text:
            orig_text = cq.message.reply_to_message.text.strip()
        else:
            orig_text = user_last_text.get(user_id, "")

        try:
            await cq.message.edit_text(
                build_panel_text(user_id, len(orig_text)),
                reply_markup=build_tts_panel_keyboard(user_id)
            )
        except Exception:
            pass

    # အသံနမူနာ စမ်းနားထောင်ခြင်း
    elif data == "preview_voice":
        v_data, rate, pitch = resolve_rate_pitch(conf)
        v_name = clean_voice_name(v_data["name"])
        sample_text = f"မင်္ဂလာပါခင်ဗျာ။ {v_name} ရဲ့ အသံစမ်းသပ်မှု ဖြစ်ပါတယ်။"
        sample_file = f"sample_{user_id}_{uuid.uuid4().hex[:6]}.mp3"
        await cq.answer("🔊 စမ်းသပ်သံ ထုတ်ပေးနေပါသည်...")

        try:
            await synthesize_speech(sample_text, v_data, rate, pitch, sample_file)
            await client.send_audio(
                chat_id=cq.message.chat.id,
                audio=sample_file,
                title=f"Sample - {v_name}",
                caption=f"🔊 **စမ်းသပ်သံ:** `{v_name}`\n⚡ Speed: `{rate}` | 🌈 Pitch: `{pitch}`"
            )
        except Exception as e:
            await cq.message.reply(f"❌ စမ်းသပ်သံ ထုတ်ရာတွင် Error: `{str(e)}`")
        finally:
            if os.path.exists(sample_file):
                os.remove(sample_file)

    # 🚀 အသံထုတ်မည် (Generate Audio)
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
        v_name = clean_voice_name(v_data["name"])
        await cq.answer("⏳ အသံဖိုင် စတင်ထုတ်လုပ်နေပါပြီ...")

        status_msg = await cq.message.reply("⏳ **အသံပြောင်းလဲနေပါသည်... ခေတ္တစောင့်ပေးပါ...**")
        out_file = f"tts_{user_id}_{uuid.uuid4().hex[:8]}.mp3"

        try:
            await synthesize_speech(text, v_data, rate, pitch, out_file)

            caption_text = (
                f"🗣️ **အသံ:** `{v_name}`\n"
                f"⚡ **Speed:** `{rate}` | 🌈 **Pitch:** `{pitch}`\n"
                f"📝 **စာလုံးရေ:** `{len(text)}` လုံး"
            )

            await client.send_audio(
                chat_id=cq.message.chat.id,
                audio=out_file,
                title=f"{v_name} - Burmese TTS",
                caption=caption_text,
                reply_to_message_id=cq.message.reply_to_message.id if cq.message.reply_to_message else None
            )
            await status_msg.delete()

        except Exception as e:
            await status_msg.edit_text(f"❌ အသံထုတ်ရာတွင် Error ဖြစ်ပွားပါသည်: `{str(e)}`")

        finally:
            if os.path.exists(out_file):
                os.remove(out_file)

if __name__ == "__main__":
    print("✅ 14-Voice Burmese TTS Bot is online!")
    app.run()
