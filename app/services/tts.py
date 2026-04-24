import numpy as np
import sounddevice as sd
from piper import PiperVoice
from app.config import TTS_MODEL_PATH, TTS_CONFIGURATION

_voice = None


def preload_voice() -> None:
    global _voice
    if _voice is None:
        _voice = PiperVoice.load(TTS_MODEL_PATH)
        print("TTS voice loaded and ready.")


def speak(text: str) -> sd.OutputStream:
    preload_voice()
    output_stream = None

    for chunk in _voice.synthesize(text, syn_config=TTS_CONFIGURATION):
        audio = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)

        if output_stream is None:
            output_stream = sd.OutputStream(
                samplerate=chunk.sample_rate,
                channels=chunk.sample_channels,
                dtype="int16",
            )
            output_stream.start()

        output_stream.write(audio.reshape(-1, chunk.sample_channels))

    return output_stream
