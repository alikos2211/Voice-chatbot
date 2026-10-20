import base64
import logging

import requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from bot.chatbot import Chatbot
from voice.speach_to_text import transcribe_bytes
from voice.text_to_speach import synthesize

log = logging.getLogger(__name__)
app = FastAPI(title="Voice Chatbot")

sessions: dict[str, Chatbot] = {}   # one chat history per browser session


def get_bot(session_id: str) -> Chatbot:
    if session_id not in sessions:
        sessions[session_id] = Chatbot()
    return sessions[session_id]


@app.post("/api/voice-chat")
def voice_chat(session_id: str = Form(...), audio: UploadFile = File(...)):
    try:
        text = transcribe_bytes(audio.file.read(), audio.filename or "voice.webm")
    except requests.RequestException as e:
        log.exception("STT failed")
        raise HTTPException(502, f"Speech-to-text service error: {e}")

    if not text:
        raise HTTPException(422, "No speech detected")

    reply = get_bot(session_id).chat(text)

    audio_b64 = ""
    if not reply.startswith("["):          # don't read error messages aloud
        try:
            audio_b64 = base64.b64encode(synthesize(reply)).decode()
        except requests.RequestException:
            log.exception("TTS failed")    # still return the text answer

    return {"user_text": text, "bot_text": reply, "audio_b64": audio_b64}


@app.post("/api/chat")                      # text-only, handy for testing
def chat(session_id: str = Form(...), message: str = Form(...)):
    return {"bot_text": get_bot(session_id).chat(message)}


@app.post("/api/clear")
def clear(session_id: str = Form(...)):
    if session_id in sessions:
        sessions[session_id].clear_history()
    return {"ok": True}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")