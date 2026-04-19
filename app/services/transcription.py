import whisper

from app.config import MODEL_NAME

_model = whisper.load_model(MODEL_NAME)


def transcribe_audio(audio_data) -> str:
    result = _model.transcribe(audio_data, language="en", fp16=False)
    return result["text"]
