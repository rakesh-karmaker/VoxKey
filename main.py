from app.core.recorder_app import RecorderApp
from app.services.transcription import Transcriber


def main():
    transcriber = Transcriber()
    RecorderApp(transcriber).run()


if __name__ == "__main__":
    main()
