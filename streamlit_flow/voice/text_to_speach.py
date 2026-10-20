import os
import re

import requests

PIPER_URL = os.getenv("PIPER_URL", "http://localhost:5000/synthesize")


def clean(text: str) -> str:
    """Remove markdown symbols that sound bad when read aloud."""
    return re.sub(r"[*#`_>]", "", text).strip()


def synthesize(text: str) -> bytes:
    """Return WAV bytes. No playback, no files."""
    text = clean(text)
    if not text:
        return b""
    r = requests.post(PIPER_URL, json={"text": text}, timeout=60)
    r.raise_for_status()
    return r.content


def speak(text: str, output_path: str = "output.wav") -> str | None:
    """Synthesize `text` and save it as a WAV file.

    Returns the path of the WAV file, or None if there was nothing to say.
    """
    wav = synthesize(text)
    if not wav:
        return None
    with open(output_path, "wb") as f:
        f.write(wav)
    return output_path


def speak_file(filepath: str = "bot_answer.txt", output_path: str = "output.wav") -> str | None:
    """Read a text file and save its spoken version to `output_path`.

    Returns the WAV path, or None if the text file is empty/missing.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except FileNotFoundError:
        return None

    if not text:
        return None
    return speak(text, output_path)