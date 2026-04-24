import os
from piper import SynthesisConfig

# Whisper model configuration
MODEL_NAME = "base"
DEVICE = "cpu"  # "cuda" if a GPU is available, otherwise "cpu"
COMPUTE_TYPE = "int8"
MODEL_LANGUAGE = "en"

# Audio recording configuration
SAMPLE_RATE = 16000
CHANNELS = 1

# TTS configuration
TTS_MODEL_PATH = (
    os.path.dirname(os.path.dirname(__file__))
    + "/tts-model/en_US-libritts_r-medium.onnx"
)  # Path to the root of the project + relative path to the TTS model

TTS_CONFIGURATION = SynthesisConfig(
    volume=1.0,  # Adjusts the loudness of the generated speech (1.0 is normal volume, >1.0 is louder, <1.0 is quieter)
    length_scale=1.15,  # Adjusts the speed of the generated speech (1.0 is normal speed, >1.0 is slower, <1.0 is faster)
)

# Hotkeys
HOTKEY = "right shift"
QUIT_HOTKEY = "ctrl+alt+q"
