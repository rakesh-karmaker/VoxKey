from app.core.recorder_app import RecorderApp
from app.services.tts import preload_voice
from app.services.transcription import Transcriber


def main():
    preload_voice()
    transcriber = Transcriber()
    RecorderApp(transcriber).run()


if __name__ == "__main__":
    main()
