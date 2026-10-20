import hashlib

import streamlit as st


def record_audio(filename, samplerate=44100, key="mic"):
    """Streamlit version of record_audio.
    Returns True when a NEW recording was saved to `filename`, otherwise False.
    """
    audio = st.audio_input(
        "🎤 Speak",
        sample_rate=samplerate,  # allowed: 8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000
        key=key,
        label_visibility="collapsed",
    )

    if audio is None:
        return False

    audio_bytes = audio.getvalue()
    if not audio_bytes:
        return False

    # Streamlit reruns the script on every interaction, and the widget keeps the
    # last recording, so only report a recording once.
    audio_hash = hashlib.md5(audio_bytes).hexdigest()
    hash_key = f"{key}_last_hash"
    if st.session_state.get(hash_key) == audio_hash:
        return False
    st.session_state[hash_key] = audio_hash

    with open(filename, "wb") as f:
        f.write(audio_bytes)

    return True