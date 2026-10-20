import requests
from pathlib import Path

WHISPER_URL = "http://localhost:8001/v1/audio/transcriptions"
MODEL = "Systran/faster-whisper-small"

def transcribe(
    audio_path: str,
    language: str | None = None,
    output_path: str | None = None,
) -> str:
    data = {"model": MODEL}
    if language:
        data["language"] = language

    with open(audio_path, "rb") as f:
        response = requests.post(WHISPER_URL, files={"file": f}, data=data)

    response.raise_for_status()
    text = response.json()["text"]

    # default: output.wav -> output.txt
    out = Path(output_path) if output_path else Path(audio_path).with_suffix(".txt")
    out.write_text(text, encoding="utf-8")

    return text

def transcribe_bytes(audio_bytes: bytes, filename: str = "voice.webm",
                     language: str | None = None) -> str:
    data = {"model": MODEL}
    if language:
        data["language"] = language
    r = requests.post(WHISPER_URL, files={"file": (filename, audio_bytes)},
                      data=data, timeout=120)
    r.raise_for_status()
    return r.json()["text"].strip()

