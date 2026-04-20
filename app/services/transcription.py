from faster_whisper import WhisperModel
from app.config import MODEL_NAME, MODEL_LANGUAGE, DEVICE, COMPUTE_TYPE


class Transcriber:
    def __init__(self) -> None:
        print("Loading Whisper model...")
        self.model = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE)
        print("Model loaded.")

    def transcribe(self, audio_data) -> str:
        """Transcribe audio data using the Whisper model."""

        segments, _ = self.model.transcribe(
            audio_data,
            language=MODEL_LANGUAGE,
            beam_size=5,
            vad_filter=True,
        )
        text = " ".join(segment.text for segment in segments)
        return text.strip()
