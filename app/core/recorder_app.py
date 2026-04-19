import queue
import threading
import tkinter as tk

import keyboard
import numpy as np
import pyperclip
import sounddevice as sd

from app.config import CHANNELS, HOTKEY, SAMPLE_RATE
from app.services.audio import compute_audio_level
from app.services.transcription import transcribe_audio
from app.ui.overlay import RecordingOverlay


class RecorderApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.withdraw()
        self.overlay = RecordingOverlay(self.root)
        self.is_recording = False
        self.stop_event = threading.Event()
        self.recording_thread = None
        self.command_queue = queue.Queue()
        self.audio_buffer = []
        self.stream = None

        keyboard.add_hotkey(HOTKEY, lambda: self.command_queue.put("toggle"))

        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
        self.root.after(50, self.poll_commands)

    def poll_commands(self) -> None:
        while True:
            try:
                command = self.command_queue.get_nowait()
            except queue.Empty:
                break

            if command == "toggle":
                self.toggle_recording()
            elif command == "finished":
                self.overlay.animate_processing()
                threading.Thread(target=self.process_recording, daemon=True).start()
            elif command == "processing_done":
                self.overlay.hide()
            elif isinstance(command, tuple) and command[0] == "level":
                self.overlay.set_audio_level(command[1])

        self.root.after(50, self.poll_commands)

    def toggle_recording(self) -> None:
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self) -> None:
        if self.is_recording:
            return

        self.is_recording = True
        self.stop_event.clear()
        self.audio_buffer = []
        self.overlay.show()
        self.recording_thread = threading.Thread(target=self.record_audio, daemon=True)
        self.recording_thread.start()

    def stop_recording(self) -> None:
        if not self.is_recording:
            return
        self.stop_event.set()

    def record_audio(self) -> None:
        def audio_callback(indata, frames, time_info, status):
            del frames, time_info
            if status:
                print(status)

            if not self.stop_event.is_set():
                self.audio_buffer.append(indata.copy())
                self.command_queue.put(("level", compute_audio_level(indata)))

        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                callback=audio_callback,
            ) as stream:
                self.stream = stream
                while not self.stop_event.is_set():
                    sd.sleep(50)
        finally:
            self.stream = None
            self.is_recording = False
            self.command_queue.put("finished")

    def process_recording(self) -> None:
        try:
            if not self.audio_buffer:
                return

            audio_data = np.concatenate(self.audio_buffer, axis=0).squeeze().astype(np.float32)
            transcription = transcribe_audio(audio_data)
            if transcription:
                pyperclip.copy(transcription.strip())
                keyboard.press_and_release("ctrl+v")
            else:
                print("No transcription available.")
        finally:
            self.command_queue.put("processing_done")

    def cleanup(self) -> None:
        self.stop_event.set()
        keyboard.unhook_all_hotkeys()
        self.root.quit()

    def run(self) -> None:
        self.root.mainloop()
