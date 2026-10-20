import io
import re
import requests
import sounddevice as sd
import soundfile as sf

PIPER_URL = "http://localhost:5000/synthesize"

def clean(text: str) -> str:
    """Remove markdown symbols that sound bad when read aloud."""
    return re.sub(r"[*#`_>]", "", text).strip()

def speak_file(filepath="bot_answer.txt") -> None:
    """Read a text file and speak its content. Does nothing if empty/missing."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except FileNotFoundError:
        return

    if text:
        speak(text)

def synthesize(text: str) -> bytes:
    """Return WAV bytes. No playback, no files."""
    text = clean(text)
    if not text:
        return b""
    r = requests.post(PIPER_URL, json={"text": text}, timeout=60)
    r.raise_for_status()
    return r.content

def speak(text: str) -> None:
    wav = synthesize(text)
    if not wav:
        return
    data, samplerate = sf.read(io.BytesIO(wav))
    sd.play(data, samplerate)
    sd.wait()

