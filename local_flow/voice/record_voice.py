
import queue

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write


def record_audio(filename, samplerate=48000, channels=1):
    q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status)
        q.put(indata.copy())

    print("Recording... press Enter to stop.")

    with sd.InputStream(
        samplerate=samplerate,
        channels=channels,
        dtype="float32",
        callback=callback,
    ):
        input()  # Wait until Enter is pressed

    chunks = []
    while not q.empty():
        chunks.append(q.get())

    if not chunks:
        print("No audio recorded.")
        return

    audio_data = np.concatenate(chunks, axis=0)
    write(filename, samplerate, audio_data)

    print(f"Record is saved to {filename}")


record_audio("recording.wav")