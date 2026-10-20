import os
from pathlib import Path

import requests


WHISPER_URL = os.getenv("WHISPER_URL", "http://localhost:8001/v1/audio/transcriptions")
MODEL = os.getenv("WHISPER_MODEL", "Systran/faster-whisper-small")
TIMEOUT = 120  # seconds, so the Streamlit app can't hang forever if the server is down


def transcribe(
    audio_path: str,
    language: str | None = None,
    output_path: str | None = None,
) -> str:
    data = {"model": MODEL}
    if language:
        data["language"] = language

    with open(audio_path, "rb") as f:
        response = requests.post(WHISPER_URL, files={"file": f}, data=data, timeout=TIMEOUT)

    response.raise_for_status()
    text = response.json()["text"]

    # default: user_sound.wav -> user_sound.txt
    out = Path(output_path) if output_path else Path(audio_path).with_suffix(".txt")
    out.write_text(text, encoding="utf-8")

    return text


def transcribe_bytes(audio_bytes: bytes, filename: str = "voice.webm",
                     language: str | None = None) -> str:
    data = {"model": MODEL}
    if language:
        data["language"] = language
    r = requests.post(WHISPER_URL, files={"file": (filename, audio_bytes)},
                      data=data, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()["text"].strip()