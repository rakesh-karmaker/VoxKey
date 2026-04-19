# VoxKey

VoxKey is a desktop voice-to-text helper for Windows. Press a hotkey to start recording, press it again to stop, and your transcription is pasted into the active app automatically.

It uses:

- A local microphone stream via `sounddevice`
- Local Whisper transcription via `openai-whisper`
- A lightweight Tk overlay for recording/processing feedback
- Clipboard + paste automation to insert text where your cursor is

## Features

- Global hotkey toggle (`right shift`) to start/stop recording
- On-screen recording visualization and processing spinner
- Local transcription with configurable Whisper model
- Automatic paste (`Ctrl+V`) of transcribed text

## Project Structure

```text
voxkey/
├─ main.pyw
├─ requirements.txt
└─ app/
   ├─ __init__.py
   ├─ config.py
   ├─ core/
   │  ├─ __init__.py
   │  └─ recorder_app.py
   ├─ services/
   │  ├─ __init__.py
   │  ├─ audio.py
   │  └─ transcription.py
   └─ ui/
      ├─ __init__.py
      └─ overlay.py
```

## File Responsibilities

- `main.pyw`:
  - App entry point.
  - Starts `RecorderApp`.

- `app/config.py`:
  - Central app constants like model name, sample rate, channels, and hotkey.

- `app/core/recorder_app.py`:
  - Main orchestration logic.
  - Handles hotkey events, microphone lifecycle, command queue, processing, and paste flow.

- `app/services/audio.py`:
  - Audio helper functions (for example, computing input level for UI animation).

- `app/services/transcription.py`:
  - Loads Whisper model and runs transcription.

- `app/ui/overlay.py`:
  - Tkinter floating overlay for recording bars and processing spinner.

## Prerequisites

1. Python 3.10+ (recommended)
2. FFmpeg installed locally and available in PATH
3. PyTorch installed
4. OpenAI Whisper (`openai-whisper`) installed

## Installation (Windows)

1. Open a terminal in the project folder.
2. Create and activate a virtual environment.
3. Install FFmpeg.
4. Install PyTorch.
5. Install OpenAI Whisper.
6. Install project dependencies.

### 1. Create virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install FFmpeg

Choose one:

- With winget:

```powershell
winget install Gyan.FFmpeg
```

- With Chocolatey:

```powershell
choco install ffmpeg
```

Then verify:

```powershell
ffmpeg -version
```

### 3. Install PyTorch

Use the command from the official PyTorch selector:

- https://pytorch.org/get-started/locally/

### 4. Install OpenAI Whisper

```powershell
pip install openai-whisper
```

### 5. Install remaining dependencies

If `requirements.txt` exists:

```powershell
pip install -r requirements.txt
```

## Run

```powershell
python main.pyw
```

## How To Use

1. Focus any text input field (chat box, notes app, editor, etc.).
2. Press `right shift` once to start recording.
3. Press `right shift` again to stop.
4. Wait briefly while transcription completes.
5. The text is copied and pasted automatically.

## Configuration

Edit `app/config.py`:

- `MODEL_NAME = "base"` (you can try `tiny`, `small`, etc.)
- `SAMPLE_RATE = 16000`
- `CHANNELS = 1`
- `HOTKEY = "right shift"`

## Troubleshooting

- `ffmpeg` not found:
  - Ensure FFmpeg is installed and added to PATH.
  - Restart terminal after installation.

- Microphone errors:
  - Check Windows microphone permissions.
  - Ensure no app is exclusively locking the mic.

- Slow transcription:
  - Use a smaller model in `app/config.py`.
  - Install GPU-enabled PyTorch if available.

- Nothing gets pasted:
  - Make sure target app is focused.
  - Check if global hotkeys are blocked by security policies.

## Notes

- Whisper model weights are downloaded on first run.
- This app is designed for local transcription workflows.
