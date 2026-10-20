import hashlib

import streamlit as st

from bot.chatbot import Chatbot
from voice.speach_to_text import transcribe
from voice.text_to_speach import speak_file

USER_WAV = "user_sound.wav"
USER_TXT = "user_sound.txt"
BOT_TXT = "bot_answer.txt"
BOT_WAV = "output.wav"

st.set_page_config(page_title="Voice Chatbot", page_icon="🎙️", layout="centered")

# ---------- Styling the frontend ----------
CSS = """
<style>
:root {
  --bg: #f4f5f7; --card: #ffffff; --text: #1d1f23; --muted: #6b7280;
  --user: #2563eb; --bot: #eef0f4; --border: #d9dce3; --danger: #dc2626;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14161a; --card: #1e2127; --text: #e8eaed; --muted: #9aa1ad;
    --user: #3b82f6; --bot: #2a2e36; --border: #343943; --danger: #f87171;
  }
}

/* page */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  background: var(--bg) !important; color: var(--text);
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
[data-testid="stSidebar"], [data-testid="stToolbar"], footer { display: none !important; }
.block-container { max-width: 720px !important; padding-top: 1.2rem !important; padding-bottom: 7rem !important; }

/* header */
.vc-title { font-size: 20px; font-weight: 600; margin: 0; color: var(--text); padding-top: 6px; }
div[data-testid="stButton"] button {
  background: none !important; border: 1px solid var(--border) !important; color: var(--muted) !important;
  padding: 6px 12px; border-radius: 8px; font-size: 13px; min-height: 0;
}
div[data-testid="stButton"] button:hover { color: var(--danger) !important; border-color: var(--danger) !important; }

/* chat log */
.vc-log {
  height: 52vh; overflow-y: auto; background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; padding: 14px; display: flex; flex-direction: column-reverse;
}
.vc-inner { display: flex; flex-direction: column; gap: 10px; min-height: 100%; }
.vc-empty { color: var(--muted); text-align: center; margin: auto; font-size: 14px; }
.vc-msg { max-width: 80%; padding: 9px 13px; border-radius: 14px; line-height: 1.4; word-wrap: break-word; }
.vc-msg.user { align-self: flex-end; background: var(--user); color: #fff; border-bottom-right-radius: 4px; }
.vc-msg.bot { align-self: flex-start; background: var(--bot); color: var(--text); border-bottom-left-radius: 4px; }
.vc-msg.error { align-self: center; background: transparent; color: var(--danger); font-size: 13px; }

/* status line */
.vc-status { height: 22px; font-size: 13px; color: var(--muted); margin: 8px 2px 4px; }

/* mic recorder + text input */
[data-testid="stAudioInput"] > div, [data-testid="stAudioInput"] {
  background: var(--card) !important; border-radius: 10px;
}
[data-testid="stChatInput"] { background: var(--card) !important; border: 1px solid var(--border); border-radius: 10px; }
[data-testid="stChatInput"]:focus-within { border-color: var(--user); }
[data-testid="stChatInput"] textarea { color: var(--text) !important; font-size: 15px; }
[data-testid="stChatInputSubmitButton"] { background: var(--user) !important; color: #fff !important; border-radius: 8px; }
[data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] { background: var(--bg) !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def esc(text: str) -> str:
    """Escape user/bot text so it can't inject HTML (same idea as textContent in JS)."""
    return (
        str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    )


def render_log(slot, history, error=None):
    parts = []
    if not history and not error:
        parts.append('<div class="vc-empty">Type a message or record your voice and speak.</div>')
    for turn in history:
        parts.append(f'<div class="vc-msg user">{esc(turn["user"])}</div>')
        parts.append(f'<div class="vc-msg bot">{esc(turn["bot"])}</div>')
    if error:
        parts.append(f'<div class="vc-msg error">Error: {esc(error)}</div>')
    inner = "".join(parts)
    slot.markdown(f'<div class="vc-log"><div class="vc-inner">{inner}</div></div>', unsafe_allow_html=True)


# ---------- Session state ----------
if "bot" not in st.session_state:
    st.session_state.bot = Chatbot()
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "reply_audio" not in st.session_state:
    st.session_state.reply_audio = None
if "error" not in st.session_state:
    st.session_state.error = None

bot = st.session_state.bot

# ---------- Header ----------
head_left, head_right = st.columns([4, 1])
head_left.markdown('<p class="vc-title">🎙️ Voice Chatbot</p>', unsafe_allow_html=True)
if head_right.button("Clear history"):
    bot.clear_history()
    st.session_state.reply_audio = None
    st.session_state.error = None
    st.session_state.last_audio_hash = None

# ---------- Layout slots (log on top, filled after inputs are processed) ----------
log_slot = st.empty()
status_slot = st.empty()
audio = st.audio_input("🎤 Speak", label_visibility="collapsed")
user_input = st.chat_input("Type a message…")


def set_status(text: str):
    status_slot.markdown(f'<div class="vc-status">{esc(text)}</div>', unsafe_allow_html=True)


set_status("")

# ---------- Voice input ----------
if audio is not None:
    audio_bytes = audio.getvalue()
    audio_hash = hashlib.md5(audio_bytes).hexdigest()

    if audio_hash != st.session_state.last_audio_hash:  # only process new recordings
        st.session_state.last_audio_hash = audio_hash
        st.session_state.error = None
        try:
            with open(USER_WAV, "wb") as f:
                f.write(audio_bytes)

            set_status("Transcribing and thinking…")
            transcribe(USER_WAV)  # writes user_sound.txt
            reply = bot.chat_from_file(USER_TXT)

            if reply is not None:
                with open(BOT_TXT, "w", encoding="utf-8") as f:
                    f.write(reply)
                speak_file(BOT_TXT)  # writes output.wav
                st.session_state.reply_audio = BOT_WAV
            else:
                st.session_state.error = "Nothing was recognized. Try again or type a message."
        except Exception as e:
            st.session_state.error = str(e)
        set_status("")

# ---------- Text input ----------
if user_input and user_input.strip():
    st.session_state.error = None
    st.session_state.reply_audio = None
    set_status("Bot is thinking…")
    try:
        bot.chat(user_input.strip())
    except Exception as e:
        st.session_state.error = str(e)
    set_status("")

# ---------- Render chat log ----------
render_log(log_slot, bot.history, st.session_state.error)

# ---------- Play the latest spoken reply ----------
if st.session_state.reply_audio:
    st.audio(st.session_state.reply_audio, format="audio/wav", autoplay=True)